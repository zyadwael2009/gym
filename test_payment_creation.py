from app import create_app
from app.database import db
from app.models.payment import Payment, PaymentAuditLog
from app.models.customer import Customer
from app.models.user import User
from app.models.subscription import Subscription
import secrets
import string
from datetime import date

app = create_app()
app.app_context().push()

print("\n" + "="*70)
print("           TESTING PAYMENT CREATION")
print("="*70 + "\n")

# Check if tables exist
try:
    payment_count = Payment.query.count()
    print(f"[OK] Payments table exists with {payment_count} records")
except Exception as e:
    print(f"[ERROR] Payments table issue: {e}")

try:
    audit_count = PaymentAuditLog.query.count()
    print(f"[OK] PaymentAuditLog table exists with {audit_count} records")
except Exception as e:
    print(f"[ERROR] PaymentAuditLog table issue: {e}")

# Find a test customer with subscription
print("\n" + "-"*70)
print("Looking for test customer...")
customer = Customer.query.first()
if not customer:
    print("[ERROR] No customers found!")
    exit(1)

print(f"[OK] Found customer: {customer.user.first_name} {customer.user.last_name}")
print(f"     Member ID: {customer.member_id}")
print(f"     Branch ID: {customer.branch_id}")

# Find a subscription
subscription = Subscription.query.filter_by(customer_id=customer.id).first()
if subscription:
    print(f"[OK] Found subscription: {subscription.subscription_number}")
    print(f"     Plan: {subscription.plan.name}")
else:
    print("[WARNING] No subscription found for customer")

# Find a staff user
staff = User.query.filter(User.role.in_(['owner', 'accountant', 'receptionist'])).first()
if not staff:
    print("[ERROR] No staff user found!")
    exit(1)

print(f"[OK] Found staff: {staff.username} ({staff.role})")

# Try to create a test payment
print("\n" + "-"*70)
print("Attempting to create test payment...")

def generate_payment_number():
    today = date.today()
    date_part = today.strftime('%y%m%d')
    random_part = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(8))
    return f"PAY{date_part}{random_part}"

try:
    payment_number = generate_payment_number()
    
    payment = Payment(
        payment_number=payment_number,
        amount=100.00,
        payment_method='cash',
        customer_id=customer.id,
        subscription_id=subscription.id if subscription else None,
        branch_id=customer.branch_id,
        service_type='subscription',
        description='Test payment',
        processed_by_id=staff.id
    )
    
    db.session.add(payment)
    db.session.flush()
    
    print(f"[OK] Payment created with ID: {payment.id}")
    
    # Try to create audit log
    print("Creating audit log...")
    audit_log = PaymentAuditLog(
        payment_id=payment.id,
        action='created',
        old_status=None,
        new_status='pending',
        performed_by_id=staff.id,
        notes="Test payment creation"
    )
    db.session.add(audit_log)
    
    db.session.commit()
    
    print(f"[OK] Test payment created successfully!")
    print(f"     Payment Number: {payment.payment_number}")
    print(f"     Amount: ${payment.amount}")
    print(f"     Status: {payment.status}")
    
    # Clean up test payment
    print("\nCleaning up test payment...")
    db.session.delete(audit_log)
    db.session.delete(payment)
    db.session.commit()
    print("[OK] Test payment cleaned up")
    
except Exception as e:
    db.session.rollback()
    print(f"\n[ERROR] Failed to create payment!")
    print(f"Error type: {type(e).__name__}")
    print(f"Error message: {str(e)}")
    import traceback
    print("\nFull traceback:")
    traceback.print_exc()

print("\n" + "="*70 + "\n")
