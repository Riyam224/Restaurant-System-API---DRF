# Testing AI Insights (Phase 2) 🤖

Quick guide to test the new AI-powered natural language insights.

## Prerequisites

1. Server running: `python manage.py runserver`
2. Admin user with token
3. Some test data (use `python seed_test_data.py` if needed)

---

## Method 1: Swagger UI (EASIEST) ⭐

1. **Open:** http://localhost:8000/api/docs/
2. **Login & Authorize** (see [QUICKSTART_ANALYTICS.md](QUICKSTART_ANALYTICS.md))
3. **Scroll to "AI Insights" section**
4. **Try these endpoints:**

### A. What Happened Today?

**Endpoint:** `GET /api/v1/analytics/insights/today/`

1. Click "Try it out"
2. (Optional) Enter a date like `2026-01-16`
3. Click "Execute"

**You'll see:**
```json
{
  "headline": "📈 Growth Continues",
  "summary": "Revenue increased by 22% to $450 with 15 orders...",
  "insights": [
    "Coupons drove 8 orders",
    "Top seller: Pizza (12 orders)"
  ]
}
```

---

### B. Explain Why (Metric Changes)

**Endpoint:** `GET /api/v1/analytics/insights/explain/`

**Parameters:**
- `metric`: revenue, orders, or users
- `days`: 30 (default)

1. Click "Try it out"
2. Enter metric: `revenue`
3. Enter days: `30`
4. Click "Execute"

**You'll see:**
```json
{
  "explanation": "Revenue has increased substantially by 25.5%...",
  "contributing_factors": [
    "Higher order volume",
    "Successful coupon campaigns"
  ]
}
```

---

### C. Business Insights

**Endpoint:** `GET /api/v1/analytics/insights/business/`

1. Click "Try it out"
2. Enter days: `30`
3. Click "Execute"

**You'll see:**
```json
{
  "overview": "Over the past 30 days, revenue is up 25.5%...",
  "opportunities": [
    "Strong growth momentum - consider expanding marketing"
  ],
  "recommendations": [
    "Implement combo deals or minimum order promotions"
  ]
}
```

---

## Method 2: cURL Commands

### Login First
```bash
TOKEN=$(curl -X POST http://localhost:8000/api/v1/analytics/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"your_password"}' \
  | jq -r '.access')
```

### Test "What Happened Today?"
```bash
curl -X GET "http://localhost:8000/api/v1/analytics/insights/today/" \
  -H "Authorization: Bearer $TOKEN" \
  | jq
```

### Test "Explain Revenue Change"
```bash
curl -X GET "http://localhost:8000/api/v1/analytics/insights/explain/?metric=revenue&days=30" \
  -H "Authorization: Bearer $TOKEN" \
  | jq
```

### Test "Business Insights"
```bash
curl -X GET "http://localhost:8000/api/v1/analytics/insights/business/?days=30" \
  -H "Authorization: Bearer $TOKEN" \
  | jq
```

---

## Method 3: Python Script

```python
import requests

BASE_URL = "http://localhost:8000"

# Login
login_response = requests.post(
    f"{BASE_URL}/api/v1/auth/login/",
    json={"username": "admin", "password": "your_password"}
)
token = login_response.json()['access']
headers = {"Authorization": f"Bearer {token}"}

# 1. What happened today?
today = requests.get(
    f"{BASE_URL}/api/v1/analytics/insights/today/",
    headers=headers
)
print("📊 Today's Summary:")
print(f"  {today.json()['headline']}")
print(f"  {today.json()['summary']}")
print()

# 2. Why did revenue change?
explain = requests.get(
    f"{BASE_URL}/api/v1/analytics/insights/explain/?metric=revenue",
    headers=headers
)
print("💡 Revenue Explanation:")
print(f"  {explain.json()['explanation']}")
print(f"  Trend: {explain.json()['trend']}")
print()

# 3. Business insights
business = requests.get(
    f"{BASE_URL}/api/v1/analytics/insights/business/",
    headers=headers
)
print("🎯 Business Recommendations:")
for rec in business.json()['recommendations']:
    print(f"  • {rec}")
```

---

## Expected Outputs

### 1. Daily Summary ("What Happened Today?")

**With Data:**
```
📈 Growth Continues

Revenue increased by 22.5% to $450.00 with 15 orders (up 25.0%).
Average order value increased to $30.00.

Insights:
• Coupons drove 8 orders, with $40.00 in discounts
• Top seller: Margherita Pizza (12 orders)
• 5 orders currently being processed
```

**With No Data:**
```
📊 Steady Progress

Revenue held steady at $0.00 with 0 orders.
```

---

### 2. Metric Explanation ("Why?")

**Growing Revenue:**
```
Metric: revenue
Trend: increasing
Change: +25.5%

Explanation:
Revenue has increased substantially by 25.5% compared to
the previous 30-day period.

Contributing Factors:
• Higher order volume
• Successful coupon campaigns
• Strong user engagement
```

**Stable Metric:**
```
Metric: orders
Trend: stable

Explanation:
Orders has remained relatively stable over the past 30 days,
showing consistent performance.
```

---

### 3. Business Insights

**Strong Performance:**
```
Period: Last 30 days

Overview:
Over the past 30 days, revenue is up 25.5% to $12,500.00
with 150 orders. You have 500 total users with 75 active
in this period (45.5% conversion rate).

Opportunities:
• Strong growth momentum - consider expanding marketing efforts
• Conversion rate could be improved - focus on user engagement

Recommendations:
• Improve user onboarding and first-time purchase incentives
• Implement combo deals or minimum order promotions
```

---

## Testing Different Scenarios

### Scenario 1: Test with Different Dates
```bash
curl -X GET "http://localhost:8000/api/v1/analytics/insights/today/?date=2026-01-15" \
  -H "Authorization: Bearer $TOKEN"
```

### Scenario 2: Test Different Metrics
```bash
# Revenue
curl "http://localhost:8000/api/v1/analytics/insights/explain/?metric=revenue" \
  -H "Authorization: Bearer $TOKEN"

# Orders
curl "http://localhost:8000/api/v1/analytics/insights/explain/?metric=orders" \
  -H "Authorization: Bearer $TOKEN"

# Users
curl "http://localhost:8000/api/v1/analytics/insights/explain/?metric=users" \
  -H "Authorization: Bearer $TOKEN"
```

### Scenario 3: Test Different Time Periods
```bash
# Last 7 days
curl "http://localhost:8000/api/v1/analytics/insights/business/?days=7" \
  -H "Authorization: Bearer $TOKEN"

# Last 90 days
curl "http://localhost:8000/api/v1/analytics/insights/business/?days=90" \
  -H "Authorization: Bearer $TOKEN"
```

---

## Automated Test

Run the full test suite:

```bash
python manage.py test analytics.tests.AIInsightsTestCase --verbosity=2
```

Expected output:
```
test_what_happened_today_endpoint ... ok
test_explain_metric_revenue ... ok
test_business_insights_endpoint ... ok
...

Ran 9 tests in 2.5s
OK
```

---

## Troubleshooting

### Empty/No Data Responses

If you get empty insights:
1. Create test data: `python seed_test_data.py`
2. Verify orders exist: Check `/api/v1/analytics/orders/status/`

### "Metric parameter is required"

Make sure to include the metric parameter:
```bash
# ❌ Wrong
/api/v1/analytics/insights/explain/

# ✅ Correct
/api/v1/analytics/insights/explain/?metric=revenue
```

### Caching Issues

Insights are cached for 1 hour. To see fresh data:
1. Wait 1 hour, or
2. Restart the server, or
3. Clear cache: `python manage.py shell` then `from django.core.cache import cache; cache.clear()`

---

## Real Examples

Try asking these business questions:

1. **"What happened today?"**
   → `/insights/today/`

2. **"Why is revenue up/down?"**
   → `/insights/explain/?metric=revenue`

3. **"What should I focus on?"**
   → `/insights/business/`

4. **"Why are orders increasing?"**
   → `/insights/explain/?metric=orders`

---

## Next Steps

1. ✅ Test all 3 endpoints
2. ✅ Try different parameters (dates, metrics, days)
3. ✅ Integrate into your dashboard
4. 📊 Use insights to make business decisions!

See [ANALYTICS_PHASE_2.md](docs/ANALYTICS_PHASE_2.md) for full documentation.
