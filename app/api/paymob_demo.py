"""Demo payment page for testing Paymob integration"""
from flask import Blueprint, request, render_template_string, redirect, url_for
from datetime import datetime

demo_bp = Blueprint('paymob_demo', __name__)

DEMO_PAYMENT_PAGE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Demo Payment - Paymob</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }
        .container {
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            max-width: 400px;
            width: 100%;
            padding: 40px 30px;
            text-align: center;
        }
        .logo {
            width: 80px;
            height: 80px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 50%;
            margin: 0 auto 20px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 40px;
            color: white;
        }
        h1 {
            color: #333;
            margin-bottom: 10px;
            font-size: 24px;
        }
        .subtitle {
            color: #666;
            margin-bottom: 30px;
            font-size: 14px;
        }
        .amount {
            font-size: 48px;
            font-weight: bold;
            color: #667eea;
            margin: 20px 0;
        }
        .currency {
            font-size: 24px;
            color: #999;
        }
        .info {
            background: #f5f5f5;
            border-radius: 10px;
            padding: 15px;
            margin: 20px 0;
            text-align: right;
        }
        .info-row {
            display: flex;
            justify-content: space-between;
            padding: 8px 0;
            border-bottom: 1px solid #e0e0e0;
        }
        .info-row:last-child {
            border-bottom: none;
        }
        .info-label {
            color: #666;
            font-size: 14px;
        }
        .info-value {
            color: #333;
            font-weight: 600;
            font-size: 14px;
        }
        .btn {
            width: 100%;
            padding: 15px;
            border: none;
            border-radius: 10px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            margin: 10px 0;
            transition: transform 0.2s, box-shadow 0.2s;
        }
        .btn:active {
            transform: scale(0.98);
        }
        .btn-success {
            background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
            color: white;
            box-shadow: 0 4px 15px rgba(56, 239, 125, 0.4);
        }
        .btn-success:hover {
            box-shadow: 0 6px 20px rgba(56, 239, 125, 0.6);
        }
        .btn-danger {
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            color: white;
            box-shadow: 0 4px 15px rgba(245, 87, 108, 0.4);
        }
        .btn-danger:hover {
            box-shadow: 0 6px 20px rgba(245, 87, 108, 0.6);
        }
        .demo-badge {
            display: inline-block;
            background: #ff9800;
            color: white;
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
            margin-bottom: 20px;
        }
        .loading {
            display: none;
            margin: 20px 0;
        }
        .spinner {
            border: 3px solid #f3f3f3;
            border-top: 3px solid #667eea;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 0 auto;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="logo">💳</div>
        <div class="demo-badge">وضع التجربة - DEMO MODE</div>
        <h1>إتمام عملية الدفع</h1>
        <p class="subtitle">مرحباً بك في نظام الدفع التجريبي</p>
        
        <div class="amount">{{ amount }}<span class="currency">جنيه</span></div>
        
        <div class="info">
            <div class="info-row">
                <span class="info-value">{{ plan_name }}</span>
                <span class="info-label">الباقة</span>
            </div>
            <div class="info-row">
                <span class="info-value">{{ plan_duration }} يوم</span>
                <span class="info-label">المدة</span>
            </div>
            <div class="info-row">
                <span class="info-value">بطاقة ائتمان</span>
                <span class="info-label">طريقة الدفع</span>
            </div>
            <div class="info-row">
                <span class="info-value">{{ payment_id }}</span>
                <span class="info-label">رقم العملية</span>
            </div>
        </div>
        
        <div class="loading" id="loading">
            <div class="spinner"></div>
            <p style="margin-top: 10px; color: #666;">جاري معالجة الدفع...</p>
        </div>
        
        <form id="paymentForm" action="{{ callback_url }}" method="POST">
            <input type="hidden" name="success" value="true">
            <input type="hidden" name="order_id" value="{{ order_id }}">
            <input type="hidden" name="amount_cents" value="{{ amount_cents }}">
            <input type="hidden" name="payment_id" value="{{ payment_id }}">
            
            <button type="button" class="btn btn-success" onclick="processPayment(true)">
                ✓ تأكيد الدفع ({{ amount }} جنيه)
            </button>
            
            <button type="button" class="btn btn-danger" onclick="processPayment(false)">
                ✗ إلغاء العملية
            </button>
        </form>
        
        <p style="color: #999; font-size: 12px; margin-top: 20px;">
            هذه صفحة تجريبية لاختبار النظام<br>
            لا يتم خصم أي مبالغ فعلية
        </p>
    </div>
    
    <script>
        function processPayment(success) {
            document.getElementById('loading').style.display = 'block';
            document.getElementById('paymentForm').style.display = 'none';
            
            // Simulate payment processing delay
            setTimeout(function() {
                if (success) {
                    // Redirect to success page
                    window.location.href = '{{ response_url }}?success=true&order_id={{ order_id }}&payment_id={{ payment_id }}';
                } else {
                    // Redirect to failure page
                    window.location.href = '{{ response_url }}?success=false&order_id={{ order_id }}&payment_id={{ payment_id }}';
                }
            }, 1500);
        }
    </script>
</body>
</html>
"""

@demo_bp.route('/demo/payment', methods=['GET'])
def demo_payment():
    """Demo payment page"""
    # Get payment details from query params
    token = request.args.get('token', '')
    payment_id = request.args.get('payment_id', 'DEMO')
    amount = request.args.get('amount', '500')
    plan_name = request.args.get('plan_name', 'اشتراك شهري')
    plan_duration = request.args.get('plan_duration', '30')
    
    # Extract order_id from token (format: demo_token_TIMESTAMP)
    order_id = f"DEMO-{token.split('_')[-1]}" if '_' in token else "DEMO-12345"
    
    # Calculate amount in cents
    try:
        amount_cents = int(float(amount) * 100)
    except:
        amount_cents = 50000
    
    return render_template_string(
        DEMO_PAYMENT_PAGE,
        amount=amount,
        plan_name=plan_name,
        plan_duration=plan_duration,
        payment_id=payment_id,
        order_id=order_id,
        amount_cents=amount_cents,
        callback_url=url_for('paymob_demo.demo_callback', _external=True),
        response_url=url_for('paymob.payment_response', _external=True)
    )

@demo_bp.route('/demo/callback', methods=['POST'])
def demo_callback():
    """Handle demo payment callback"""
    success = request.form.get('success') == 'true'
    order_id = request.form.get('order_id')
    payment_id = request.form.get('payment_id')
    
    # Redirect to response page
    return redirect(url_for('paymob.payment_response', 
                          success=success, 
                          order_id=order_id,
                          payment_id=payment_id,
                          _external=True))
