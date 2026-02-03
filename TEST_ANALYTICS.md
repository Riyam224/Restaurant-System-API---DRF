###  Testing Analytics - Quick Start Guide

## Prerequisites

1. **Create a superuser** (if you don't have one):
```bash
source venv/bin/activate
python manage.py createsuperuser
```

Follow the prompts to create an admin account.

## Option 1: Using the Browser (Swagger UI)

### Step 1: Start the Server
```bash
source venv/bin/activate
python manage.py runserver
```

### Step 2: Open Swagger UI
Navigate to: **http://localhost:8000/api/docs/**

### Step 3: Authenticate
1. Click the **"Authorize"** button (top right)
2. Login to get your JWT token:
   - Go to the `/api/v1/auth/login/` endpoint
   - Click "Try it out"
   - Enter your credentials:
     ```json
     {
       "username": "your_admin_username",
       "password": "your_password"
     }
     ```
   - Click "Execute"
   - Copy the `access` token from the response

3. Click "Authorize" again and paste:
   ```
   Bearer YOUR_ACCESS_TOKEN
   ```

### Step 4: Test Analytics Endpoints

Scroll down to the **"Analytics"** section in Swagger UI. You'll see all 8 endpoints:

1. **Dashboard KPIs** - `/api/v1/analytics/dashboard/`
2. **Revenue Metrics** - `/api/v1/analytics/revenue/metrics/`
3. **Daily Revenue** - `/api/v1/analytics/revenue/daily/`
4. **Order Status** - `/api/v1/analytics/orders/status/`
5. **User Metrics** - `/api/v1/analytics/users/metrics/`
6. **Product Performance** - `/api/v1/analytics/products/performance/`
7. **Coupon Performance** - `/api/v1/analytics/coupons/performance/`
8. **Review Metrics** - `/api/v1/analytics/reviews/metrics/`

Click any endpoint, then "Try it out" and "Execute" to see the results!

---

## Option 2: Using cURL (Command Line)

### Step 1: Login and Get Token
```bash
curl -X POST http://localhost:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "your_admin_username",
    "password": "your_password"
  }'
```

**Copy the access token from the response.**

### Step 2: Test Dashboard KPIs
```bash
curl -X GET "http://localhost:8000/api/v1/analytics/dashboard/?days=30" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Step 3: Test Revenue Metrics
```bash
curl -X GET "http://localhost:8000/api/v1/analytics/revenue/metrics/" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Step 4: Test Daily Revenue (for charts)
```bash
curl -X GET "http://localhost:8000/api/v1/analytics/revenue/daily/" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Step 5: Test User Metrics
```bash
curl -X GET "http://localhost:8000/api/v1/analytics/users/metrics/" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Step 6: Test Product Performance
```bash
curl -X GET "http://localhost:8000/api/v1/analytics/products/performance/" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

---

## Option 3: Using Python Requests

Create a test script:

```python
import requests

# Base URL
BASE_URL = "http://localhost:8000"

# Step 1: Login
login_response = requests.post(
    f"{BASE_URL}/api/v1/auth/login/",
    json={
        "username": "your_admin_username",
        "password": "your_password"
    }
)

# Get the access token
token = login_response.json()['access']
headers = {"Authorization": f"Bearer {token}"}

# Step 2: Get Dashboard KPIs
dashboard = requests.get(
    f"{BASE_URL}/api/v1/analytics/dashboard/?days=30",
    headers=headers
)
print("Dashboard KPIs:", dashboard.json())

# Step 3: Get Revenue Metrics
revenue = requests.get(
    f"{BASE_URL}/api/v1/analytics/revenue/metrics/",
    headers=headers
)
print("\nRevenue Metrics:", revenue.json())

# Step 4: Get Daily Revenue
daily = requests.get(
    f"{BASE_URL}/api/v1/analytics/revenue/daily/",
    headers=headers
)
print("\nDaily Revenue:", daily.json())

# Step 5: Get User Metrics
users = requests.get(
    f"{BASE_URL}/api/v1/analytics/users/metrics/",
    headers=headers
)
print("\nUser Metrics:", users.json())

# Step 6: Get Product Performance
products = requests.get(
    f"{BASE_URL}/api/v1/analytics/products/performance/",
    headers=headers
)
print("\nProduct Performance:", products.json())
```

---

## Option 4: Using Postman

### Step 1: Import to Postman
1. Open Postman
2. Create a new request
3. Set method to POST
4. URL: `http://localhost:8000/api/v1/auth/login/`
5. Body → raw → JSON:
   ```json
   {
     "username": "your_admin_username",
     "password": "your_password"
   }
   ```
6. Send and copy the `access` token

### Step 2: Test Analytics Endpoints
1. Create a new GET request
2. URL: `http://localhost:8000/api/v1/analytics/dashboard/`
3. Headers → Add:
   - Key: `Authorization`
   - Value: `Bearer YOUR_ACCESS_TOKEN`
4. Send!

**Try these URLs:**
- `/api/v1/analytics/dashboard/?days=30`
- `/api/v1/analytics/revenue/metrics/`
- `/api/v1/analytics/revenue/daily/`
- `/api/v1/analytics/orders/status/`
- `/api/v1/analytics/users/metrics/`
- `/api/v1/analytics/products/performance/`
- `/api/v1/analytics/coupons/performance/`
- `/api/v1/analytics/reviews/metrics/`

---

## Sample Data (If Database is Empty)

If you need test data to see meaningful analytics:

### Create Test Data via Django Shell
```bash
source venv/bin/activate
python manage.py shell
```

Then run:
```python
from django.contrib.auth import get_user_model
from orders.models import Order, OrderItem
from addresses.models import Address
from decimal import Decimal

User = get_user_model()

# Create a test user
user = User.objects.create_user(username='testuser', password='test123')

# Create an address
address = Address.objects.create(
    user=user,
    label='Home',
    street='123 Main St',
    city='New York',
    building='Apt 5',
    lat=40.7128,
    lng=-74.0060
)

# Create some paid orders
for i in range(10):
    Order.objects.create(
        user=user,
        address=address,
        subtotal=Decimal('100.00'),
        discount_amount=Decimal('10.00'),
        total_price=Decimal('90.00'),
        payment_status='paid',
        status='delivered'
    )

print("✅ Test data created!")
```

---

## Expected Response Examples

### Dashboard KPIs Response
```json
{
  "period_days": 30,
  "revenue": {
    "current": 900.00,
    "previous": 0.00,
    "growth_percentage": 100.0
  },
  "orders": {
    "current": 10,
    "previous": 0,
    "growth_percentage": 100.0
  },
  "average_order_value": 90.00,
  "total_users": 2,
  "active_users": 1,
  "conversion_rate": 50.0,
  "order_status": [...]
}
```

### Revenue Metrics Response
```json
{
  "total_revenue": 900.00,
  "total_orders": 10,
  "average_order_value": 90.00,
  "total_discount": 100.00,
  "gross_revenue": 1000.00,
  "period": {
    "start": "2025-12-17T00:00:00Z",
    "end": "2026-01-16T00:00:00Z"
  }
}
```

---

## Troubleshooting

### Error: 401 Unauthorized
- You're not logged in or token expired
- Solution: Login again and get a fresh token

### Error: 403 Forbidden
- Your user is not an admin (is_staff=False)
- Solution: Make your user a staff member:
  ```bash
  python manage.py shell
  ```
  ```python
  from django.contrib.auth import get_user_model
  User = get_user_model()
  user = User.objects.get(username='your_username')
  user.is_staff = True
  user.save()
  ```

### No Data in Response
- Database might be empty
- Solution: Create test data (see "Sample Data" section above)

---

## Quick Test Command

Run the automated tests:
```bash
source venv/bin/activate
python manage.py test analytics
```

Expected output:
```
Ran 16 tests in 3.714s
OK
```

---

## Visual Testing (Admin Panel)

The analytics app is registered in Django admin at:
**http://localhost:8000/admin/**

Login with your superuser credentials to see the analytics section in the sidebar.

---

## Need Help?

Check the full documentation:
- [Analytics README](../analytics/README.md)
- [API Endpoints Documentation](./API_ENDPOINTS_ANALYTICS.md)
- [Phase 1 Summary](./ANALYTICS_PHASE_1.md)
