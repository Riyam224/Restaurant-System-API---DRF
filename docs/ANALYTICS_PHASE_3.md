# Analytics Phase 3: Anomaly Detection & Smart Alerts

**Purpose:** Intelligence, not just reporting. Detect unusual patterns and provide actionable explanations.

## Overview

Phase 3 adds intelligent anomaly detection to your restaurant analytics system. Instead of just showing numbers, it proactively identifies unusual patterns and explains WHY they might be happening.

### Key Features

1. **Revenue Anomalies** - Detects unusual spikes or drops in daily revenue
2. **Order Volume Monitoring** - Identifies abnormal order counts
3. **Coupon Abuse Detection** - Flags suspicious coupon usage patterns
4. **User Behavior Analysis** - Detects unusual customer activity

### Example Output

```
⚠️ Revenue dropped unusually on Tuesday
  Revenue was only $245.00, 65% below normal.
  Possible reason: Very few orders (4 orders).
  Recommended: Check for technical problems or delivery issues.
```

---

## Quick Start

### 1. Test the Endpoints

```bash
# Run the test script
python test_anomaly_detection.py
```

### 2. API Endpoints

**Get Anomaly Summary:**
```bash
GET /api/v1/analytics/anomalies/summary/?days=7
```

**Detect All Anomalies:**
```bash
GET /api/v1/analytics/anomalies/detect/?days=7
```

**Daily Digest:**
```bash
GET /api/v1/analytics/anomalies/digest/
```

### 3. Try in Swagger

1. Open http://localhost:8000/api/docs/
2. Find "Anomaly Detection" section
3. Try each endpoint with different parameters

---

## Anomaly Types

### 1. Revenue Anomalies

**Revenue Spike:**
- Triggered when: Daily revenue is 2x+ normal
- Severity: Info (< 3x) or Warning (≥ 3x)
- Example: "$450 revenue (3x normal $150 average)"

**Revenue Drop:**
- Triggered when: Daily revenue is < 50% of normal
- Severity: Warning (< 30%) or Info (≥ 30%)
- Example: "$50 revenue (67% below normal $150 average)"

**Configuration:**
```python
# analytics/anomaly_detection.py
REVENUE_SPIKE_THRESHOLD = 2.0  # 2x normal
REVENUE_DROP_THRESHOLD = 0.5   # 50% of normal
```

### 2. Order Volume Anomalies

**Order Spike:**
- Triggered when: Daily orders are 2x+ normal
- Severity: Info
- Possible reasons: Marketing success, weekend effect, competitor closure

**Order Drop:**
- Triggered when: Daily orders are < 50% of normal
- Severity: Warning
- Possible reasons: Technical issues, bad weather, competitor promotion

### 3. Coupon Abuse Detection

**Heavy Coupon Usage:**
- Triggered when: User exceeds 3 coupons/day over the period
- Severity: Warning
- Possible reasons: Account sharing, coupon farming, multiple accounts

**Suspicious Discounts:**
- Triggered when: Order has >90% discount
- Severity: Critical
- Possible reasons: Stacked coupons, system glitch, fraudulent activity

**Configuration:**
```python
MAX_COUPON_USES_PER_USER_PER_DAY = 3
SUSPICIOUS_DISCOUNT_PERCENTAGE = 90  # 90%+ discount
```

### 4. User Behavior Anomalies

**User Registration Spike:**
- Triggered when: New registrations are 2x+ normal
- Severity: Info
- Action: Verify registrations are legitimate (not bots)

**High-Frequency Ordering:**
- Triggered when: User places 3+ orders/day on average
- Severity: Info
- Action: Consider VIP treatment or loyalty rewards

---

## API Reference

### Detect Anomalies

**Endpoint:** `GET /api/v1/analytics/anomalies/detect/`

**Parameters:**
- `days` (int, optional): Period to analyze (1-90 days, default: 7)
- `use_ai` (bool, optional): Use Claude AI for explanations (default: false)

**Response:**
```json
{
  "summary": "⚠️ 2 warning(s) detected. Review recommended.",
  "pattern_analysis": "Multiple revenue drops suggest a broader demand issue.",
  "recommended_actions": [
    "Analyze drop causes and address service issues",
    "Check for technical problems or delivery issues"
  ],
  "anomalies": [
    {
      "type": "revenue_drop",
      "severity": "warning",
      "date": "2026-01-15",
      "title": "Revenue Drop on Tuesday",
      "description": "Revenue was only $245.00, 65% below normal.",
      "value": 245.0,
      "baseline": 700.0,
      "change_percentage": -65.0,
      "possible_reasons": [
        "Very few orders (4 orders)",
        "Early weekday slowdown"
      ],
      "ai_explanation": "Revenue dropped significantly..."
    }
  ]
}
```

### Get Anomaly Summary

**Endpoint:** `GET /api/v1/analytics/anomalies/summary/`

**Parameters:**
- `days` (int, optional): Period to analyze (1-90 days, default: 7)

**Response:**
```json
{
  "period_days": 7,
  "total_anomalies": 5,
  "severity_counts": {
    "critical": 1,
    "warning": 2,
    "info": 2
  },
  "type_counts": {
    "revenue_drop": 2,
    "coupon_abuse_high_discount": 1,
    "high_frequency_ordering": 2
  },
  "has_critical": true,
  "has_warnings": true,
  "anomalies": [/* top 10 */]
}
```

### Daily Digest

**Endpoint:** `GET /api/v1/analytics/anomalies/digest/`

**Response:**
```json
{
  "date": "2026-01-17",
  "anomaly_count": 3,
  "has_critical": false,
  "digest": "🔔 Daily Anomaly Report\n\nℹ️ INFO (3):\n  • ...",
  "anomalies": [/* all anomalies */]
}
```

---

## AI-Powered Explanations

### Enable Claude API (Optional)

For more detailed, context-aware explanations:

**1. Set up Claude API:**
```bash
export ANTHROPIC_API_KEY=sk-ant-your-key-here
```

**2. Request AI explanations:**
```bash
GET /api/v1/analytics/anomalies/detect/?days=7&use_ai=true
```

**3. Compare outputs:**

**Rule-based (free):**
> "Revenue dropped to $245.00 on Tuesday, 65% below the usual $700.00. Possible causes: Very few orders (4 orders), Early weekday slowdown."

**AI-powered (requires API key):**
> "Your restaurant experienced a significant revenue shortfall on Tuesday, bringing in only $245 compared to your typical $700 daily average. This 65% drop appears to be primarily driven by unusually low order volume—just 4 orders compared to your normal flow. The timing (early in the week) suggests this could be a natural Tuesday slowdown, but the magnitude warrants investigation. Check for any service disruptions, delivery issues, or local events that might have affected accessibility."

### Cost Considerations

- Rule-based: **Free**, instant
- AI-powered: ~$0.003 per anomaly explanation
- Recommended: Use rule-based for regular monitoring, AI for critical issues

---

## Integration Examples

### 1. Dashboard Alert Widget

```javascript
// Fetch anomaly summary for dashboard
fetch('/api/v1/analytics/anomalies/summary/?days=7', {
  headers: { 'Authorization': `Bearer ${token}` }
})
.then(res => res.json())
.then(data => {
  // Show alert badge if critical issues exist
  if (data.has_critical) {
    showAlertBadge(data.severity_counts.critical);
  }

  // Display summary
  displayAnomalySummary(data.total_anomalies, data.type_counts);
});
```

### 2. Email Notification Service

```python
# Send daily digest email
from analytics.anomaly_detection import AnomalyDetector
from analytics.anomaly_explainer import generate_daily_digest

def send_daily_anomaly_report():
    """Send daily email with detected anomalies."""
    anomalies = AnomalyDetector.detect_all_anomalies(days=1)

    if not anomalies:
        return  # No anomalies, skip email

    digest = generate_daily_digest(anomalies)

    send_email(
        to='manager@restaurant.com',
        subject='Daily Anomaly Report',
        body=digest
    )

# Run daily at 9 AM
# (use cron, celery, or django-cron)
```

### 3. Slack/Discord Webhook

```python
import requests

def send_critical_alert_to_slack(anomaly):
    """Send critical anomalies to Slack immediately."""
    if anomaly['severity'] != 'critical':
        return

    webhook_url = 'https://hooks.slack.com/services/YOUR/WEBHOOK/URL'

    message = {
        'text': f"🚨 *Critical Alert*: {anomaly['title']}",
        'attachments': [{
            'color': 'danger',
            'fields': [
                {'title': 'Description', 'value': anomaly['description']},
                {'title': 'Recommended Action', 'value': anomaly.get('recommended_action', 'N/A')}
            ]
        }]
    }

    requests.post(webhook_url, json=message)

# Call after detecting anomalies
for anomaly in anomalies:
    if anomaly['severity'] == 'critical':
        send_critical_alert_to_slack(anomaly)
```

### 4. Automated Response System

```python
def auto_respond_to_anomaly(anomaly):
    """Take automated action for certain anomalies."""

    if anomaly['type'] == 'order_drop':
        # Send notification to operations team
        notify_ops_team(anomaly)

    elif anomaly['type'] == 'coupon_abuse_high_discount':
        # Temporarily disable coupon code
        suspend_coupon(anomaly['coupon_code'])
        notify_admin(f"Suspended suspicious coupon: {anomaly['coupon_code']}")

    elif anomaly['type'] == 'coupon_abuse_heavy_usage':
        # Flag user account for review
        flag_user_for_review(anomaly['user_id'])
```

---

## Customization

### Adjust Thresholds

Edit `analytics/anomaly_detection.py`:

```python
class AnomalyDetector:
    # Make detection more sensitive
    REVENUE_SPIKE_THRESHOLD = 1.5  # 50% increase triggers alert
    REVENUE_DROP_THRESHOLD = 0.7   # 30% decrease triggers alert

    # Stricter coupon abuse detection
    MAX_COUPON_USES_PER_USER_PER_DAY = 2  # 2 coupons/day max
    SUSPICIOUS_DISCOUNT_PERCENTAGE = 75   # 75%+ discount is suspicious
```

### Add Custom Anomaly Types

```python
@staticmethod
def detect_delivery_time_anomalies(days: int = 7) -> List[Dict[str, Any]]:
    """Detect unusual delivery time patterns."""
    anomalies = []

    # Get orders with delivery times
    orders = Order.objects.filter(
        created_at__gte=timezone.now() - timedelta(days=days),
        status='delivered'
    )

    # Calculate average delivery time
    avg_time = orders.aggregate(
        avg=Avg(F('delivered_at') - F('created_at'))
    )['avg']

    # Check for slow deliveries
    slow_orders = orders.filter(
        delivered_at__gt=F('created_at') + timedelta(hours=2)
    )

    if slow_orders.count() > 10:
        anomalies.append({
            'type': 'slow_delivery',
            'severity': 'warning',
            'title': f'{slow_orders.count()} Slow Deliveries',
            'description': f'{slow_orders.count()} orders took over 2 hours to deliver.',
            'recommended_action': 'Review delivery operations and driver availability'
        })

    return anomalies
```

Then add to `detect_all_anomalies()`:

```python
delivery_anomalies = AnomalyDetector.detect_delivery_time_anomalies(days)
anomalies.extend(delivery_anomalies)
```

---

## Best Practices

### 1. Set Appropriate Thresholds

- Start with default thresholds
- Monitor for false positives
- Adjust based on your business patterns
- Different restaurants have different "normal"

### 2. Prioritize by Severity

```python
# Handle critical issues immediately
critical = [a for a in anomalies if a['severity'] == 'critical']
for anomaly in critical:
    send_immediate_alert(anomaly)

# Review warnings daily
warnings = [a for a in anomalies if a['severity'] == 'warning']
add_to_daily_report(warnings)

# Log info anomalies for patterns
info = [a for a in anomalies if a['severity'] == 'info']
log_for_trend_analysis(info)
```

### 3. Combine with Manual Review

Anomaly detection is a tool, not a replacement for human judgment:

- Review flagged anomalies in context
- Look for patterns over time
- Investigate root causes
- Update thresholds based on findings

### 4. Automate Routine Responses

```python
# Automated response rules
RESPONSE_RULES = {
    'order_drop': notify_ops_team,
    'coupon_abuse_high_discount': suspend_and_notify,
    'revenue_spike': log_success_pattern,
}

for anomaly in anomalies:
    handler = RESPONSE_RULES.get(anomaly['type'])
    if handler:
        handler(anomaly)
```

---

## Troubleshooting

### No Anomalies Detected

**Possible causes:**
- Not enough historical data (need at least 14 days)
- Thresholds too high
- Operations genuinely normal

**Solutions:**
```python
# Lower thresholds temporarily to test
REVENUE_SPIKE_THRESHOLD = 1.2  # 20% increase
```

### Too Many False Positives

**Possible causes:**
- Thresholds too low
- High natural variance in your business
- Seasonal patterns not accounted for

**Solutions:**
- Increase thresholds
- Add day-of-week adjustments
- Implement seasonal baselines

### Performance Issues

**Possible causes:**
- Large date ranges
- Many orders in database

**Solutions:**
- Limit default days to 7
- Add database indexes on created_at
- Cache anomaly results

```python
# Add caching
from django.core.cache import cache

def detect_all_anomalies_cached(days=7):
    cache_key = f'anomalies_{days}_{timezone.now().date()}'
    cached = cache.get(cache_key)
    if cached:
        return cached

    anomalies = AnomalyDetector.detect_all_anomalies(days)
    cache.set(cache_key, anomalies, 3600)  # Cache for 1 hour
    return anomalies
```

---

## Testing

### Run Test Suite

```bash
# Test all endpoints
python test_anomaly_detection.py

# Test specific anomaly type
python manage.py shell
>>> from analytics.anomaly_detection import AnomalyDetector
>>> AnomalyDetector.detect_revenue_anomalies(days=30)
```

### Create Test Anomalies

```python
# Create a revenue spike
from orders.models import Order
from django.utils import timezone

# Create many high-value orders today
for i in range(20):
    Order.objects.create(
        user=test_user,
        address=test_address,
        total_price=100,
        payment_status='paid',
        status='delivered',
        created_at=timezone.now()
    )

# Test detection
anomalies = AnomalyDetector.detect_revenue_anomalies(days=1)
```

---

## Next Steps

1. **Monitor Daily** - Check anomaly digest each morning
2. **Set Up Alerts** - Configure email/Slack notifications
3. **Adjust Thresholds** - Fine-tune based on your data
4. **Add Custom Detectors** - Create domain-specific anomaly types
5. **Enable AI** - Use Claude for critical issue explanations
6. **Automate Responses** - Set up automated actions for common issues

---

## Summary

Phase 3 adds intelligent anomaly detection that:

- ✅ Detects revenue spikes/drops automatically
- ✅ Flags suspicious coupon usage
- ✅ Identifies unusual order patterns
- ✅ Provides AI-powered explanations
- ✅ Enables proactive operations management

**Remember:** Anomaly detection is intelligence, not just reporting. Use it to catch issues before they become problems!

---

## See Also

- [Phase 2: AI Insights](ANALYTICS_PHASE_2.md) - Natural language summaries
- [Claude API Upgrade](CLAUDE_API_UPGRADE.md) - Enable AI explanations
- [Analytics API Reference](../README.md) - Full API documentation