# Analytics System - Complete Guide

## Table of Contents
1. [Quick Start](#quick-start)
2. [Features Overview](#features-overview)
3. [Setup & Testing](#setup--testing)
4. [Analytics Endpoints](#analytics-endpoints)
5. [AI-Powered Insights](#ai-powered-insights)
6. [Anomaly Detection](#anomaly-detection)
7. [Predictions](#predictions)
8. [Integration Examples](#integration-examples)
9. [Troubleshooting](#troubleshooting)

---

## Quick Start

### Get Started in 3 Minutes

#### Step 1: Create Test Data (1 minute)

```bash
# Activate virtual environment
source venv/bin/activate

# Create sample data
python seed_test_data.py
```

This creates:
- 5 test users
- 5 products
- ~90 orders over last 30 days
- 6 reviews

#### Step 2: Start Server (30 seconds)

```bash
python manage.py runserver
```

#### Step 3: Test Analytics (choose one method)

**Option A: Swagger UI (Easiest)** ⭐

1. Open: http://localhost:8000/api/schema/swagger-ui/
2. Login via `/api/v1/auth/login/` to get token
3. Click "Authorize" and enter: `Bearer YOUR_TOKEN`
4. Try `/api/v1/analytics/dashboard/`

**Option B: Automated Test Script**

```bash
python test_analytics_api.py
```

**Option C: cURL**

```bash
# Login
curl -X POST http://localhost:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"your_password"}'

# Test analytics (use token from login)
curl -X GET "http://localhost:8000/api/v1/analytics/dashboard/?days=30" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## Features Overview

The analytics system provides three tiers of intelligence:

### Tier 1: Standard Analytics
- **Revenue Metrics**: Total revenue, growth trends, daily breakdowns
- **Order Analytics**: Status distribution, completion rates
- **User Metrics**: Total users, active users, conversion rates
- **Product Performance**: Best sellers, revenue by product
- **Coupon Analytics**: Discount effectiveness, usage rates
- **Review Metrics**: Rating distribution, review counts

### Tier 2: AI-Powered Insights (Claude AI)
- **Business Insights**: Natural language summaries of performance
- **Metric Explanations**: AI explains why metrics changed
- **Opportunities**: AI-identified growth opportunities
- **Warnings**: Potential issues that need attention
- **Recommendations**: Actionable advice to improve business

### Tier 3: Advanced Features
- **Anomaly Detection**: Automatic detection of unusual patterns
- **Predictions**: Forecast tomorrow's revenue and orders
- **Optimal Timing**: Best times for promotions
- **Inventory Risks**: Predict potential stock-outs

---

## Setup & Testing

### Requirements

- Python 3.13+
- Django 4.2.11+
- Admin user account (`is_staff=True`)
- **For AI Features**: Anthropic API key

### Environment Setup

Create `.env` file:

```bash
# Required for AI features
ANTHROPIC_API_KEY=sk-ant-...

# Database
DATABASE_URL=sqlite:///db.sqlite3

# Django
DEBUG=True
SECRET_KEY=your-secret-key
```

### Create Admin User

```bash
# Method 1: Using management command
python manage.py createsuperuser

# Method 2: Via Django shell
python manage.py shell
>>> from django.contrib.auth import get_user_model
>>> User = get_user_model()
>>> User.objects.create_superuser('admin', 'admin@example.com', 'password')
```

### Running Tests

```bash
# All analytics tests
python manage.py test analytics

# Specific test
python manage.py test analytics.tests.TestDashboardKPIs

# With coverage
coverage run --source='analytics' manage.py test analytics
coverage report
coverage html
```

---

## Analytics Endpoints

**Base URL**: `/api/v1/analytics/`

**Authentication**: All endpoints require admin authentication (`is_staff=True`)

### 1. Dashboard KPIs

```http
GET /api/v1/analytics/dashboard/?days=30
```

**Query Parameters**:
- `days` (optional): Number of days to analyze (default: 30)

**Response**:
```json
{
  "period_days": 30,
  "revenue": {
    "current": 12500.00,
    "previous": 10000.00,
    "growth_percentage": 25.0
  },
  "orders": {
    "current": 450,
    "previous": 380,
    "growth_percentage": 18.4
  },
  "average_order_value": 27.78,
  "total_users": 1250,
  "active_users": 380,
  "conversion_rate": 36.0,
  "order_status": [
    {"status": "pending", "count": 25},
    {"status": "preparing", "count": 15},
    {"status": "on_the_way", "count": 10},
    {"status": "delivered", "count": 400}
  ]
}
```

### 2. Revenue Analytics

#### Revenue Metrics

```http
GET /api/v1/analytics/revenue/metrics/?start_date=2026-01-01&end_date=2026-01-31
```

**Query Parameters**:
- `start_date` (optional): Start date (YYYY-MM-DD)
- `end_date` (optional): End date (YYYY-MM-DD)
- Defaults to last 30 days if not provided

**Response**:
```json
{
  "total_revenue": 12500.00,
  "total_orders": 450,
  "average_order_value": 27.78,
  "total_discount": 1250.00,
  "gross_revenue": 13750.00,
  "period": {
    "start": "2026-01-01T00:00:00Z",
    "end": "2026-01-31T23:59:59Z"
  }
}
```

#### Daily Revenue

```http
GET /api/v1/analytics/revenue/daily/?start_date=2026-01-01&end_date=2026-01-31
```

**Response**:
```json
{
  "dates": ["2026-01-01", "2026-01-02", "2026-01-03", ...],
  "revenue": [450.00, 520.00, 385.00, ...],
  "order_count": [15, 18, 12, ...]
}
```

Perfect for charts!

### 3. Order Analytics

```http
GET /api/v1/analytics/orders/status/
```

**Response**:
```json
{
  "by_status": [
    {
      "status": "pending",
      "status_display": "Pending",
      "count": 25,
      "percentage": 5.6
    },
    {
      "status": "delivered",
      "status_display": "Delivered",
      "count": 400,
      "percentage": 88.9
    }
  ],
  "total_orders": 450
}
```

### 4. User Analytics

```http
GET /api/v1/analytics/users/metrics/?days=30
```

**Response**:
```json
{
  "total_users": 1250,
  "new_users": 85,
  "active_users": 380,
  "retention_rate": 72.5,
  "average_orders_per_user": 2.3,
  "top_customers": [
    {
      "user_id": 42,
      "username": "john_doe",
      "total_spent": 1250.00,
      "order_count": 28
    }
  ]
}
```

### 5. Product Performance

```http
GET /api/v1/analytics/products/performance/?limit=10
```

**Query Parameters**:
- `limit` (optional): Number of top products (default: 20)

**Response**:
```json
{
  "top_products": [
    {
      "product_id": 10,
      "product_name": "Classic Burger",
      "total_revenue": 2500.00,
      "total_orders": 200,
      "units_sold": 350,
      "average_rating": 4.5
    }
  ],
  "total_products": 45,
  "average_revenue_per_product": 277.78
}
```

### 6. Coupon Performance

```http
GET /api/v1/analytics/coupons/performance/
```

**Response**:
```json
{
  "coupons": [
    {
      "code": "SAVE10",
      "usage_count": 150,
      "total_discount": 750.00,
      "revenue_impact": 7500.00,
      "roi": 10.0
    }
  ],
  "total_discount_given": 1250.00,
  "orders_with_coupons": 180,
  "coupon_usage_rate": 40.0
}
```

### 7. Review Metrics

```http
GET /api/v1/analytics/reviews/metrics/
```

**Response**:
```json
{
  "total_reviews": 850,
  "average_rating": 4.3,
  "distribution": {
    "5": 520,
    "4": 210,
    "3": 85,
    "2": 25,
    "1": 10
  },
  "verified_purchases": 720,
  "pending_approval": 15
}
```

---

## AI-Powered Insights

**Powered by**: Claude Sonnet 4.5 by Anthropic

### 1. Business Insights

Get a comprehensive AI analysis of your business performance.

```http
GET /api/v1/analytics/insights/business/?days=30
```

**Response**:
```json
{
  "overview": "Revenue increased 25% compared to last month with strong growth in dinner orders. Order volume is up 18%, driven by successful coupon campaigns.",
  "opportunities": [
    "Peak ordering time is 6-8 PM. Consider happy hour promotion to capture early dinner crowd.",
    "Top 3 products generate 60% of revenue. Expand similar items or create combo deals.",
    "Cart abandonment rate is 35%. Implement abandoned cart email campaigns."
  ],
  "warnings": [
    "Delivery times averaging 45min, above target of 30min. May impact customer satisfaction.",
    "Coupon usage up 40% but margin pressure increasing. Review discount strategy.",
    "Low stock alerts on 3 popular items. Risk of missed sales opportunities."
  ],
  "recommendations": [
    "Launch a loyalty program to improve retention and increase order frequency",
    "Optimize delivery routing to reduce wait times and improve customer experience",
    "A/B test checkout flow to reduce abandonment and increase conversion",
    "Introduce time-limited flash sales during slow periods (2-4 PM)",
    "Bundle low-margin items with high-margin products to protect profitability"
  ]
}
```

### 2. Explain Metric Changes

Ask AI to explain why a specific metric changed.

```http
GET /api/v1/analytics/insights/explain/?metric=revenue&days=30
```

**Query Parameters**:
- `metric`: revenue, orders, or users
- `days`: Analysis period (default: 30)

**Response**:
```json
{
  "metric": "revenue",
  "period_days": 30,
  "current_value": 12500.00,
  "previous_value": 10000.00,
  "change_percentage": 25.0,
  "explanation": "Revenue increased substantially by 25% over the past 30 days. This growth is primarily driven by higher order volume (up 18%) and successful coupon campaigns that attracted new customers without significantly eroding margins.",
  "contributing_factors": [
    "Order volume increased from 380 to 450 orders (+18%)",
    "Average order value remained stable at $27.78",
    "Successful coupon 'SAVE10' drove 150 orders",
    "New product launches performed well",
    "Weekend sales showed strong growth"
  ]
}
```

### 3. Today's Summary

Quick daily summary in natural language.

```http
GET /api/v1/analytics/insights/today/?date=2026-01-16
```

**Response**:
```json
{
  "date": "2026-01-16",
  "headline": "📈 Strong Performance",
  "summary": "Today saw revenue of $485 from 18 orders, up 8% from yesterday. The Classic Burger was the top seller with 12 orders. Coupons were used in 40% of orders.",
  "insights": [
    "Peak order time was 6:30 PM with 5 orders in 30 minutes",
    "Average order value $26.94, slightly below 30-day average",
    "Top seller: Classic Burger (12 orders, $150 revenue)",
    "Coupon 'SAVE10' drove 7 orders today",
    "3 new customers made their first order"
  ]
}
```

### How AI Insights Work

The system uses **Claude Sonnet 4.5** to:
1. Fetch analytics data from your database
2. Calculate trends and comparisons
3. Send structured data to Claude AI
4. Claude analyzes patterns and generates insights
5. Returns natural language explanations

**Caching**: AI responses are cached for 30-60 minutes to save costs and improve speed.

**Fallback**: If Claude API is unavailable, the system uses rule-based insights.

---

## Anomaly Detection

Automatically detect unusual patterns in your data.

```http
GET /api/v1/analytics/anomalies/detect/?days=7&use_ai=true
```

**Query Parameters**:
- `days`: Detection window (default: 7)
- `use_ai`: Use AI for explanations (default: true)

**Response**:
```json
{
  "anomalies": [
    {
      "type": "revenue_spike",
      "severity": "warning",
      "date": "2026-01-15",
      "metric": "daily_revenue",
      "value": 1500.00,
      "expected": 450.00,
      "deviation": 233.3,
      "explanation": "Revenue spike detected on Jan 15. This is 3.3x higher than the average daily revenue. Likely causes: successful promotion campaign, viral social media post, or special event. Monitor if pattern continues."
    },
    {
      "type": "order_drop",
      "severity": "critical",
      "date": "2026-01-14",
      "metric": "daily_orders",
      "value": 3,
      "expected": 15,
      "deviation": -80.0,
      "explanation": "Significant order drop on Jan 14. Only 3 orders compared to average of 15. Potential causes: website downtime, delivery issues, or competing promotion. Investigate immediately."
    },
    {
      "type": "coupon_abuse",
      "severity": "warning",
      "date": "2026-01-13",
      "metric": "coupon_usage",
      "value": 12,
      "explanation": "Unusual coupon usage pattern detected. Code 'SAVE10' used 12 times by same user. May indicate sharing or abuse. Consider usage limits per user."
    }
  ],
  "total_anomalies": 3,
  "detection_period": {
    "start": "2026-01-09",
    "end": "2026-01-16"
  }
}
```

### Anomaly Types Detected

| Type | Description | Severity Threshold |
|------|-------------|-------------------|
| **revenue_spike** | Revenue >3x average | Warning |
| **revenue_drop** | Revenue <50% average | Critical |
| **order_spike** | Orders >3x average | Warning |
| **order_drop** | Orders <50% average | Critical |
| **coupon_abuse** | >50% usage in one day | Warning |
| **rating_drop** | Average rating drops >1 star | Warning |
| **stock_out** | Popular product out of stock | Critical |

---

## Predictions

Forecast future metrics using historical data.

### 1. Tomorrow's Forecast

```http
GET /api/v1/analytics/predictions/tomorrow/
```

**Response**:
```json
{
  "date": "2026-01-17",
  "predicted_revenue": 485.50,
  "predicted_orders": 18,
  "confidence": 0.85,
  "method": "moving_average",
  "based_on": {
    "last_7_days_avg": 465.00,
    "last_30_days_avg": 450.00,
    "trend": "increasing"
  }
}
```

### 2. Optimal Promotion Times

Find the best times to run promotions.

```http
GET /api/v1/analytics/predictions/promo-times/
```

**Response**:
```json
{
  "recommendations": [
    {
      "time_slot": "14:00-16:00",
      "day_of_week": "weekday",
      "reason": "Lowest order volume - promotional opportunity",
      "average_orders": 2,
      "potential_lift": "3-5 orders"
    },
    {
      "time_slot": "18:00-20:00",
      "day_of_week": "weekend",
      "reason": "Peak demand - maximize revenue with premium items",
      "average_orders": 25,
      "potential_lift": "5-8 orders"
    }
  ]
}
```

### 3. Inventory Risks

Predict potential stock-outs.

```http
GET /api/v1/analytics/predictions/inventory-risks/
```

**Response**:
```json
{
  "at_risk_products": [
    {
      "product_id": 10,
      "product_name": "Classic Burger",
      "current_stock": 15,
      "daily_avg_sales": 12,
      "days_until_stockout": 1.2,
      "recommended_reorder": 100,
      "risk_level": "critical"
    }
  ],
  "total_at_risk": 1
}
```

---

## Integration Examples

### Python / Django

```python
import requests

# Configuration
BASE_URL = "http://localhost:8000"
headers = {"Authorization": f"Bearer {access_token}"}

# Get dashboard KPIs
response = requests.get(
    f"{BASE_URL}/api/v1/analytics/dashboard/?days=30",
    headers=headers
)
data = response.json()
print(f"Revenue: ${data['revenue']['current']}")
print(f"Growth: {data['revenue']['growth_percentage']}%")

# Get AI insights
response = requests.get(
    f"{BASE_URL}/api/v1/analytics/insights/business/?days=30",
    headers=headers
)
insights = response.json()
print(insights['overview'])
```

### Flutter / Dart

```dart
import 'package:http/http.dart' as http;
import 'dart:convert';

class AnalyticsService {
  final String baseUrl = 'http://localhost:8000';
  final String accessToken;

  AnalyticsService(this.accessToken);

  Future<Map<String, dynamic>> getDashboard({int days = 30}) async {
    final response = await http.get(
      Uri.parse('$baseUrl/api/v1/analytics/dashboard/?days=$days'),
      headers: {
        'Authorization': 'Bearer $accessToken',
        'Content-Type': 'application/json',
      },
    );

    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    } else {
      throw Exception('Failed to load analytics');
    }
  }

  Future<Map<String, dynamic>> getBusinessInsights({int days = 30}) async {
    final response = await http.get(
      Uri.parse('$baseUrl/api/v1/analytics/insights/business/?days=$days'),
      headers: {
        'Authorization': 'Bearer $accessToken',
      },
    );

    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    } else {
      throw Exception('Failed to load insights');
    }
  }
}

// Usage
final analytics = AnalyticsService(userToken);
final dashboard = await analytics.getDashboard(days: 30);
print('Revenue: \$${dashboard['revenue']['current']}');
```

### JavaScript / React

```javascript
class AnalyticsAPI {
  constructor(baseUrl, accessToken) {
    this.baseUrl = baseUrl;
    this.accessToken = accessToken;
  }

  async getDashboard(days = 30) {
    const response = await fetch(
      `${this.baseUrl}/api/v1/analytics/dashboard/?days=${days}`,
      {
        headers: {
          'Authorization': `Bearer ${this.accessToken}`,
          'Content-Type': 'application/json',
        },
      }
    );

    if (!response.ok) {
      throw new Error('Failed to fetch analytics');
    }

    return await response.json();
  }

  async getAIInsights(days = 30) {
    const response = await fetch(
      `${this.baseUrl}/api/v1/analytics/insights/business/?days=${days}`,
      {
        headers: {
          'Authorization': `Bearer ${this.accessToken}`,
        },
      }
    );

    return await response.json();
  }
}

// Usage in React component
const AnalyticsDashboard = () => {
  const [data, setData] = useState(null);
  const api = new AnalyticsAPI('http://localhost:8000', userToken);

  useEffect(() => {
    api.getDashboard(30).then(setData);
  }, []);

  return (
    <div>
      <h2>Revenue: ${data?.revenue.current}</h2>
      <p>Growth: {data?.revenue.growth_percentage}%</p>
    </div>
  );
};
```

---

## Troubleshooting

### "403 Forbidden" Error

**Problem**: Your user doesn't have admin access.

**Solution**:
```bash
python manage.py shell
```

```python
from django.contrib.auth import get_user_model
User = get_user_model()
user = User.objects.get(username='your_username')
user.is_staff = True
user.save()
print("User is now an admin!")
```

### AI Insights Not Working

**Problem**: Claude API key missing or invalid.

**Check**:
1. `.env` file has `ANTHROPIC_API_KEY=sk-ant-...`
2. API key is valid and has credits
3. Check logs: `tail -f logs/restaurant.log`

**Test manually**:
```bash
python manage.py shell
```

```python
from analytics.claude_insights import ClaudeInsightsService
service = ClaudeInsightsService()
result = service.get_business_insights(days=7)
print(result)
```

### No Data in Analytics

**Problem**: Database is empty.

**Solution**: Create test data:
```bash
python seed_test_data.py
```

Or manually:
```bash
python manage.py shell
```

```python
from django.contrib.auth import get_user_model
from orders.models import Order
from addresses.models import Address
from decimal import Decimal

User = get_user_model()
user = User.objects.create_user('testuser', password='test123')
address = Address.objects.create(
    user=user,
    label='Home',
    street='123 Main St',
    city='New York',
    building='Apt 5'
)

# Create orders
for i in range(10):
    Order.objects.create(
        user=user,
        address=address,
        subtotal=Decimal('100.00'),
        total_price=Decimal('90.00'),
        payment_status='paid',
        status='delivered'
    )
```

### Slow Response Times

**Problem**: Analytics queries are slow.

**Solutions**:
1. **Check database indexes**: Ensure indexes exist on `orders.created_at`, `orders.status`
2. **Enable caching**: Already configured, but verify it's active
3. **Reduce date ranges**: Use shorter periods (7 days instead of 30)
4. **Check database size**: Very large databases may need optimization

```bash
# Check query performance
python manage.py dbshell
```

```sql
EXPLAIN ANALYZE SELECT * FROM orders_order WHERE created_at >= '2026-01-01';
```

### Token Expired

**Problem**: 401 Unauthorized after some time.

**Solution**: Access tokens expire after 30 minutes. Refresh them:

```python
import requests

# Refresh token
response = requests.post(
    'http://localhost:8000/api/v1/auth/refresh/',
    json={'refresh': refresh_token}
)
new_access_token = response.json()['access']
```

---

## Performance Tips

### 1. Use Caching

All analytics endpoints use Django's cache framework:
- **Dashboard**: 5 minutes
- **AI Insights**: 30-60 minutes
- **Charts Data**: 5 minutes

### 2. Optimize Date Ranges

```python
# ✅ Good: Specific short range
?start_date=2026-01-01&end_date=2026-01-07

# ❌ Slow: Very long range
?start_date=2020-01-01&end_date=2026-01-31
```

### 3. Pagination for Large Datasets

```python
# For product performance
/api/v1/analytics/products/performance/?limit=10  # Fast

# Instead of
/api/v1/analytics/products/performance/?limit=1000  # Slow
```

### 4. Batch Requests

```python
# ✅ Good: Parallel requests
import asyncio

async def fetch_all_analytics():
    tasks = [
        fetch_dashboard(),
        fetch_revenue(),
        fetch_products(),
    ]
    return await asyncio.gather(*tasks)

# ❌ Bad: Sequential requests
dashboard = fetch_dashboard()
revenue = fetch_revenue()  # Waits for dashboard
products = fetch_products()  # Waits for revenue
```

---

## API Reference Summary

| Endpoint | Purpose | Response Time | Cache |
|----------|---------|---------------|-------|
| `/dashboard/` | Main KPIs | ~50ms | 5 min |
| `/revenue/metrics/` | Revenue summary | ~40ms | 5 min |
| `/revenue/daily/` | Daily breakdown | ~100ms | 5 min |
| `/orders/status/` | Order stats | ~30ms | 5 min |
| `/users/metrics/` | User stats | ~60ms | 5 min |
| `/products/performance/` | Top products | ~80ms | 5 min |
| `/coupons/performance/` | Coupon stats | ~50ms | 5 min |
| `/reviews/metrics/` | Review stats | ~40ms | 5 min |
| `/insights/business/` | AI insights | ~2-3s (first) | 30 min |
| `/insights/explain/` | AI explanation | ~2s (first) | 30 min |
| `/anomalies/detect/` | Find anomalies | ~500ms | 15 min |
| `/predictions/tomorrow/` | Forecast | ~100ms | 30 min |

---

## Changelog

### Version 3.0 (Phase 3)
- ✅ AI-powered business insights
- ✅ Natural language explanations
- ✅ Anomaly detection with AI
- ✅ Predictive analytics
- ✅ Optimal promotion timing

### Version 2.0 (Phase 2)
- ✅ AI insights integration
- ✅ Claude Sonnet 4.5 support
- ✅ Metric change explanations
- ✅ Daily summaries

### Version 1.0 (Phase 1)
- ✅ Dashboard KPIs
- ✅ Revenue analytics
- ✅ Order analytics
- ✅ User metrics
- ✅ Product performance
- ✅ Coupon analytics
- ✅ Review metrics
- ✅ Admin-only permissions

---

## Support

- **Swagger UI**: http://localhost:8000/api/schema/swagger-ui/
- **Logs**: `logs/restaurant.log`
- **Claude API Status**: https://status.anthropic.com
- **Test Scripts**: `test_analytics_api.py`, `test_insights_now.py`

---

**Analytics System Version**: 3.0
**AI Model**: Claude Sonnet 4.5
**Last Updated**: February 14, 2026
**Status**: Production Ready ✅
