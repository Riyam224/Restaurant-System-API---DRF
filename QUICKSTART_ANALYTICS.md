# Analytics Quick Start 🚀

Get the analytics system up and running in 3 minutes!

## Step 1: Create Test Data (1 min)

Create sample orders, users, and products to test analytics:

```bash
source venv/bin/activate
python seed_test_data.py
```

This will create:
- 5 test users
- 5 products
- ~90 orders over the last 30 days
- 6 reviews

## Step 2: Start the Server (30 seconds)

```bash
python manage.py runserver
```

## Step 3: View Analytics (3 options)

### Option A: Interactive API Docs (EASIEST) ⭐

1. **Open browser:** http://localhost:8000/api/docs/
2. **Login to get token:**
   - Find `/api/v1/auth/login/` endpoint
   - Click "Try it out"
   - Enter credentials (your admin username/password)
   - Click "Execute"
   - Copy the `access` token

3. **Authorize:**
   - Click "Authorize" button (🔓 top right)
   - Enter: `Bearer YOUR_ACCESS_TOKEN`
   - Click "Authorize"

4. **Test Analytics:**
   - Scroll to "Analytics" section
   - Try `/api/v1/analytics/dashboard/`
   - Click "Try it out" → "Execute"
   - See your analytics! 📊

### Option B: Automated Test Script

```bash
python test_analytics_api.py
```

Enter your admin credentials when prompted.

### Option C: Manual cURL

```bash
# Login
curl -X POST http://localhost:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "your_password"}'

# Copy the token, then:
curl -X GET "http://localhost:8000/api/v1/analytics/dashboard/" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

---

## What You'll See

### Dashboard KPIs Response:
```json
{
  "period_days": 30,
  "revenue": {
    "current": 1234.56,
    "previous": 0.00,
    "growth_percentage": 100.0
  },
  "orders": {
    "current": 67,
    "previous": 0,
    "growth_percentage": 100.0
  },
  "average_order_value": 18.42,
  "total_users": 5,
  "active_users": 3,
  "conversion_rate": 60.0
}
```

---

## All 8 Analytics Endpoints

Once authenticated, try these:

1. **Dashboard** - `/api/v1/analytics/dashboard/?days=30`
2. **Revenue** - `/api/v1/analytics/revenue/metrics/`
3. **Daily Revenue** - `/api/v1/analytics/revenue/daily/`
4. **Orders** - `/api/v1/analytics/orders/status/`
5. **Users** - `/api/v1/analytics/users/metrics/`
6. **Products** - `/api/v1/analytics/products/performance/`
7. **Coupons** - `/api/v1/analytics/coupons/performance/`
8. **Reviews** - `/api/v1/analytics/reviews/metrics/`

---

## Troubleshooting

### "403 Forbidden"
Your user needs admin access:
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

### "No admin user"
Create one:
```bash
python manage.py createsuperuser
```

### "Connection refused"
Make sure the server is running:
```bash
python manage.py runserver
```

---

## 🎉 That's it!

You now have a fully functional analytics system with:
- ✅ Real-time revenue metrics
- ✅ User statistics
- ✅ Product performance
- ✅ Order tracking
- ✅ Growth percentages

See [TEST_ANALYTICS.md](TEST_ANALYTICS.md) for detailed testing guide.
