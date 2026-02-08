# API Documentation

## Base URL
All API endpoints are prefixed with `/api`

## Authentication
Most endpoints require JWT authentication. Include the token in the Authorization header:
```
Authorization: Bearer <jwt-token>
```

## Response Format
All responses follow this structure:
```json
{
    "success": true,
    "data": {...},
    "message": "Operation successful"
}
```

Error responses:
```json
{
    "success": false,
    "error": "Error message",
    "code": 400
}
```

## Endpoints Summary

### Authentication
- `POST /api/auth/login` - User login
- `POST /api/auth/logout` - User logout

### Branch Management
- `GET /api/branches` - List branches
- `POST /api/branches` - Create branch (Owner only)
- `GET /api/branches/{id}` - Get branch details
- `PUT /api/branches/{id}` - Update branch
- `DELETE /api/branches/{id}` - Delete branch (Owner only)

### Customer Management
- `GET /api/customers` - List customers
- `POST /api/customers` - Create customer
- `GET /api/customers/{id}` - Get customer details
- `PUT /api/customers/{id}` - Update customer
- `DELETE /api/customers/{id}` - Delete customer

### Subscription Management
- `GET /api/subscriptions` - List subscriptions
- `POST /api/subscriptions` - Create subscription
- `GET /api/subscriptions/{id}` - Get subscription details
- `PUT /api/subscriptions/{id}` - Update subscription
- `PUT /api/subscriptions/{id}/status` - Update subscription status

### Payment Management
- `GET /api/payments` - List payments
- `POST /api/payments` - Record payment
- `GET /api/payments/{id}` - Get payment details

### Attendance
- `POST /api/attendance/checkin` - Customer check-in
- `POST /api/attendance/checkout/{id}` - Customer check-out
- `GET /api/attendance/customer/{customer_id}` - Get customer attendance
- `GET /api/attendance/branch/{branch_id}` - Get branch attendance

### Dashboard
- `GET /api/dashboard/overview` - Get dashboard metrics

### Complaints
- `GET /api/complaints` - List complaints
- `POST /api/complaints` - Submit complaint
- `GET /api/complaints/{id}` - Get complaint details
- `PUT /api/complaints/{id}/resolve` - Resolve complaint

## Role-Based Access

### Owner
- Full access to all branches and features
- Can create/delete branches
- Can manage all users

### Branch Manager
- Access to assigned branch only
- Can manage customers, subscriptions, payments
- Can view branch analytics

### Receptionist
- Customer management
- Attendance tracking
- Basic subscription operations

### Accountant
- Payment management
- Financial reports
- Subscription billing

### Customer
- View own profile and subscription
- View attendance history
- Submit complaints

## Testing
Use the test interface at `/test` to manually test all endpoints with different user roles.