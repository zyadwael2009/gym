"""Paymob Payment Gateway API Routes"""
from flask import Blueprint, request, jsonify
from app.database import db
from app.models.customer import Customer
from app.models.subscription import Subscription
from app.models.payment import Payment
from app.services.paymob_service import PaymobService
from app.auth import require_customer, require_staff
from datetime import datetime

paymob_bp = Blueprint('paymob', __name__)

@paymob_bp.route('/test', methods=['GET'])
def test_endpoint():
    """Test endpoint to verify blueprint is working"""
    return jsonify({'message': 'Paymob blueprint is working!', 'success': True}), 200

@paymob_bp.route('/initiate', methods=['POST'])
@require_customer()
def initiate_payment(current_user):
    """Initiate Paymob payment for customer"""
    print(f"[PAYMOB] Initiate called by user: {current_user.id} - {current_user.email}")
    try:
        data = request.get_json()
        print(f"[PAYMOB] Request data: {data}")
        
        # Validate required fields
        amount = data.get('amount')
        payment_method = data.get('payment_method', 'card')  # 'card' or 'wallet'
        plan_duration = data.get('plan_duration')  # Duration in days
        plan_name = data.get('plan_name', 'Subscription Plan')
        
        if not amount or not plan_duration:
            return jsonify({'error': 'amount and plan_duration are required'}), 400
        
        # Get customer profile
        customer = Customer.query.filter_by(user_id=current_user.id).first()
        if not customer:
            return jsonify({'error': 'Customer profile not found'}), 404
        
        # Prepare customer data for Paymob
        customer_data = {
            'first_name': current_user.first_name,
            'last_name': current_user.last_name,
            'email': current_user.email,
            'phone': current_user.phone or '+201000000000'
        }
        
        # Initiate payment with Paymob
        print(f"[PAYMOB API] Initiating payment for customer {customer.id}: {amount} EGP")
        payment_data = PaymobService.initiate_payment(
            amount=amount,
            customer_data=customer_data,
            subscription_id=None,  # Will be set after payment
            payment_method=payment_method
        )
        
        print(f"[PAYMOB API] Payment data received: {payment_data}")
        
        if not payment_data:
            print(f"[PAYMOB API] ERROR: No payment data returned from Paymob service")
            return jsonify({'error': 'Failed to initiate payment with Paymob'}), 500
        
        # Store pending payment in database
        from app.api.payment import generate_payment_number
        payment_number = generate_payment_number()
        
        payment = Payment(
            payment_number=payment_number,
            amount=amount,
            payment_method='card' if payment_method == 'card' else 'upi',
            customer_id=customer.id,
            subscription_id=None,  # Will be created after payment
            branch_id=customer.branch_id,
            service_type='subscription',
            description=f'Paymob payment for {plan_name} ({plan_duration} days)',
            reference_number=str(payment_data['order_id']),
            processed_by_id=current_user.id,
            status='pending'
        )
        
        db.session.add(payment)
        db.session.flush()  # Get payment.id
        
        # Store plan details in payment notes for later subscription creation
        payment.notes = f'plan_duration:{plan_duration}|plan_name:{plan_name}'
        
        db.session.commit()
        print(f"[PAYMOB API] Payment record created: ID={payment.id}")
        
        # Add payment details to demo URL (for demo mode only)
        iframe_url = payment_data['iframe_url']
        if 'demo/payment' in iframe_url:
            iframe_url += f"&payment_id={payment.id}&plan_name={plan_name}&plan_duration={plan_duration}"
        
        return jsonify({
            'success': True,
            'payment_id': payment.id,
            'payment_token': payment_data['payment_token'],
            'iframe_url': iframe_url,
            'order_id': payment_data['order_id']
        }), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"[PAYMOB API] Exception occurred: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        print(f"[PAYMOB] Initiate error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': 'Failed to initiate payment', 'details': str(e)}), 500

@paymob_bp.route('/callback', methods=['POST'])
def payment_callback():
    """Handle Paymob payment callback (webhook)"""
    try:
        data = request.get_json()
        print(f"[PAYMOB] Received callback: {data}")
        
        # Verify HMAC
        query_params = data.get('obj', {})
        if not PaymobService.verify_callback(query_params):
            print("[PAYMOB] HMAC verification failed!")
            return jsonify({'error': 'Invalid HMAC'}), 403
        
        # Parse callback data
        transaction_info = PaymobService.parse_callback_data(data)
        
        # Find payment by reference number (order_id)
        payment = Payment.query.filter_by(
            reference_number=str(transaction_info['order_id'])
        ).first()
        
        if not payment:
            print(f"[PAYMOB] Payment not found for order {transaction_info['order_id']}")
            return jsonify({'error': 'Payment not found'}), 404
        
        # Update payment status
        if transaction_info['success'] and not transaction_info['error_occured']:
            payment.status = 'completed'
            payment.payment_time = datetime.utcnow()
            
            # Create and activate subscription from payment notes
            if payment.notes and 'plan_duration:' in payment.notes:
                try:
                    # Parse plan details from notes
                    parts = payment.notes.split('|')
                    plan_duration = int(parts[0].split(':')[1])
                    plan_name = parts[1].split(':')[1] if len(parts) > 1 else 'Subscription'
                    
                    # Create new subscription
                    from datetime import timedelta
                    subscription = Subscription(
                        customer_id=payment.customer_id,
                        plan_id=None,  # No plan_id for custom Paymob subscriptions
                        start_date=date.today(),
                        end_date=date.today() + timedelta(days=plan_duration),
                        amount_paid=payment.amount,
                        payment_method='online',
                        status='active',
                        is_active=True,
                        notes=f'Paymob payment - {plan_name}'
                    )
                    db.session.add(subscription)
                    db.session.flush()
                    
                    # Link payment to subscription
                    payment.subscription_id = subscription.id
                    print(f"[PAYMOB] Created subscription {subscription.id} for {plan_duration} days")
                except Exception as e:
                    print(f"[PAYMOB] Error creating subscription: {e}")
                    import traceback
                    traceback.print_exc()
        else:
            payment.status = 'failed'
            print(f"[PAYMOB] Payment failed for order {transaction_info['order_id']}")
        
        db.session.commit()
        
        return jsonify({'success': True}), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"[PAYMOB] Callback error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': 'Callback processing failed'}), 500

@paymob_bp.route('/response', methods=['GET'])
def payment_response():
    """Handle payment response redirect - shows HTML page for WebView"""
    from flask import render_template_string
    
    # Get query parameters
    success = request.args.get('success', 'false') == 'true'
    order_id = request.args.get('order_id', '')
    payment_id = request.args.get('payment_id', '')
    
    # Simple HTML page that will close the webview
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Payment {'Success' if success else 'Failed'}</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                display: flex;
                align-items: center;
                justify-content: center;
                min-height: 100vh;
                margin: 0;
                background: {'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' if success else 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)'};
            }}
            .container {{
                background: white;
                padding: 40px;
                border-radius: 20px;
                text-align: center;
                box-shadow: 0 20px 60px rgba(0,0,0,0.3);
                max-width: 90%;
            }}
            .icon {{
                font-size: 80px;
                margin-bottom: 20px;
            }}
            h1 {{
                color: #333;
                margin-bottom: 10px;
            }}
            p {{
                color: #666;
                margin: 10px 0;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="icon">{'✓' if success else '✗'}</div>
            <h1>{'تم الدفع بنجاح!' if success else 'فشلت عملية الدفع'}</h1>
            <p>{'سيتم تفعيل اشتراكك الآن' if success else 'يرجى المحاولة مرة أخرى'}</p>
            <p style="font-size: 12px; color: #999; margin-top: 20px;">سيتم إغلاق هذه النافذة تلقائياً...</p>
        </div>
        <script>
            // Signal to Flutter app that payment is complete
            setTimeout(function() {{
                window.location.href = 'flutter://payment-complete?success={str(success).lower()}&payment_id={payment_id}';
            }}, 2000);
        </script>
    </body>
    </html>
    """
    return render_template_string(html)

@paymob_bp.route('/status/<int:payment_id>', methods=['GET'])
@require_customer()
def check_payment_status(payment_id, current_user):
    """Check payment status"""
    try:
        payment = Payment.query.get_or_404(payment_id)
        
        # Verify ownership
        if payment.customer.user_id != current_user.id:
            return jsonify({'error': 'Access denied'}), 403
        
        return jsonify({
            'payment_id': payment.id,
            'status': payment.status,
            'amount': float(payment.amount),
            'payment_method': payment.payment_method,
            'created_at': payment.created_at.isoformat(),
            'subscription': {
                'id': payment.subscription_id,
                'status': payment.subscription.status if payment.subscription else None
            } if payment.subscription else None
        }), 200
        
    except Exception as e:
        print(f"[PAYMOB] Status check error: {str(e)}")
        return jsonify({'error': 'Failed to check status'}), 500
