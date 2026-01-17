# Upgrading AI Insights to Claude API

This guide shows you how to upgrade from rule-based insights to actual AI-powered insights using Anthropic's Claude API.

## Table of Contents
- [Why Upgrade?](#why-upgrade)
- [Quick Start](#quick-start)
- [Setup](#setup)
- [Integration Options](#integration-options)
- [Testing](#testing)
- [Cost Considerations](#cost-considerations)
- [Best Practices](#best-practices)

---

## Why Upgrade?

### Current (Rule-Based)
- ✅ Fast and free
- ✅ No API dependencies
- ❌ Fixed templates and logic
- ❌ Cannot adapt to new patterns
- ❌ Generic insights

### With Claude API
- ✅ Dynamic, context-aware insights
- ✅ Natural language understanding
- ✅ Adapts to your specific business
- ✅ Can reason about complex patterns
- ❌ Requires API key (costs money)
- ❌ Slightly slower (API call latency)

---

## Quick Start

### 1. Install Dependencies

```bash
pip install anthropic>=0.40.0
```

Or use the updated requirements.txt:

```bash
pip install -r requirements.txt
```

### 2. Get API Key

1. Sign up at https://console.anthropic.com/
2. Create an API key
3. Note your key (starts with `sk-ant-`)

### 3. Set Environment Variable

**Option A: .env file (recommended)**

Add to your `.env` file:
```bash
ANTHROPIC_API_KEY=sk-ant-your-key-here
```

**Option B: Export in terminal**

```bash
export ANTHROPIC_API_KEY=sk-ant-your-key-here
```

**Option C: Django settings**

Add to `config/settings.py`:
```python
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
```

### 4. Test It Works

```bash
python analytics/claude_insights.py
```

You should see:
```
✅ Claude API is available
Testing business insights...
{
  "overview": "...",
  "opportunities": [...],
  ...
}
```

---

## Setup

### Step 1: Environment Configuration

Create or update your `.env` file:

```bash
# AI Configuration
ANTHROPIC_API_KEY=sk-ant-your-api-key-here

# Optional: Customize model
ANTHROPIC_MODEL=claude-sonnet-4-5-20250929
```

### Step 2: Update Django Settings

Add to `config/settings.py`:

```python
# AI/ML Configuration
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
ANTHROPIC_MODEL = os.getenv('ANTHROPIC_MODEL', 'claude-sonnet-4-5-20250929')

# Feature flags
USE_CLAUDE_INSIGHTS = bool(ANTHROPIC_API_KEY)  # Auto-enable if API key exists
```

### Step 3: Verify Installation

```python
from analytics.claude_insights import ClaudeInsightsService

if ClaudeInsightsService.is_available():
    print("✅ Ready to use Claude API")
else:
    print("❌ Missing: anthropic package or ANTHROPIC_API_KEY")
```

---

## Integration Options

You have three options for integrating Claude API:

### Option 1: Replace Existing Service (Recommended for Production)

Update `analytics/ai_insights.py` to use Claude when available:

```python
from analytics.claude_insights import ClaudeInsightsService

class AIInsightsService:
    @staticmethod
    def get_business_insights(days: int = 30) -> Dict[str, Any]:
        # Get KPIs
        kpis = AnalyticsQueries.get_dashboard_kpis(days=days)

        # Use Claude if available, fallback to rule-based
        if ClaudeInsightsService.is_available():
            try:
                return ClaudeInsightsService.get_business_insights(kpis)
            except Exception as e:
                logger.error(f"Claude API failed: {e}")
                # Fallback to rule-based

        # Original rule-based logic...
        return {...}
```

### Option 2: New Endpoints (Recommended for Testing)

Add new Claude-specific endpoints alongside existing ones:

```python
# analytics/views.py

class ClaudeBusinessInsightsView(APIView):
    """Claude-powered business insights (requires API key)"""

    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        if not ClaudeInsightsService.is_available():
            return Response(
                {'error': 'Claude API not configured'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )

        days = int(request.query_params.get('days', 30))
        kpis = AnalyticsQueries.get_dashboard_kpis(days=days)
        data = ClaudeInsightsService.get_business_insights(kpis)
        return Response(data)
```

Update `analytics/urls.py`:

```python
urlpatterns = [
    # ... existing endpoints ...

    # Claude-powered endpoints
    path('insights/claude/business/', ClaudeBusinessInsightsView.as_view()),
]
```

### Option 3: Feature Flag (Recommended for Gradual Rollout)

Use Django settings to switch between implementations:

```python
# config/settings.py
USE_CLAUDE_INSIGHTS = os.getenv('USE_CLAUDE_INSIGHTS', 'false').lower() == 'true'

# analytics/ai_insights.py
from django.conf import settings

if settings.USE_CLAUDE_INSIGHTS:
    InsightsBackend = ClaudeInsightsService
else:
    InsightsBackend = RuleBasedInsightsService
```

---

## Testing

### Test Script

Create `test_claude_insights.py`:

```python
#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from analytics.claude_insights import ClaudeInsightsService
from analytics.queries import AnalyticsQueries

def test_claude_insights():
    """Test Claude API integration"""

    if not ClaudeInsightsService.is_available():
        print("❌ Claude API not available")
        print("Set ANTHROPIC_API_KEY environment variable")
        return

    print("✅ Claude API is available\n")

    # Get real KPIs from your database
    kpis = AnalyticsQueries.get_dashboard_kpis(days=30)

    print("Testing business insights...")
    insights = ClaudeInsightsService.get_business_insights(kpis)

    print(f"\nOverview: {insights['overview']}")
    print(f"\nOpportunities:")
    for opp in insights['opportunities']:
        print(f"  • {opp}")
    print(f"\nRecommendations:")
    for rec in insights['recommendations']:
        print(f"  • {rec}")

if __name__ == '__main__':
    test_claude_insights()
```

Run it:

```bash
python test_claude_insights.py
```

### Compare Rule-Based vs Claude

```python
# Compare both implementations
rule_based = AIInsightsService.get_business_insights(days=30)
claude_based = ClaudeInsightsService.get_business_insights(kpis)

print("Rule-based:", rule_based['overview'])
print("Claude-based:", claude_based['overview'])
```

---

## Cost Considerations

### Pricing (as of 2026)

Claude Sonnet 4.5:
- Input: $3 per million tokens (~750,000 words)
- Output: $15 per million tokens (~750,000 words)

### Estimated Costs

For a typical restaurant with 100 API calls per day:

**Per Request:**
- Input: ~500 tokens (KPI data) = $0.0015
- Output: ~300 tokens (insights) = $0.0045
- **Total per request: ~$0.006**

**Per Day (100 requests):**
- 100 requests × $0.006 = **$0.60/day**

**Per Month:**
- 30 days × $0.60 = **$18/month**

### Reducing Costs

1. **Caching** (already implemented):
   ```python
   # Insights cached for 1 hour
   cache.set(cache_key, insights, 3600)
   ```

2. **Use Haiku for simpler tasks** (5x cheaper):
   ```python
   MODEL = "claude-haiku-4-5-20250929"
   ```

3. **Batch requests** when possible

4. **Rate limiting** for non-critical endpoints

---

## Best Practices

### 1. Error Handling

Always have a fallback:

```python
try:
    insights = ClaudeInsightsService.get_business_insights(kpis)
except Exception as e:
    logger.error(f"Claude API error: {e}")
    # Fall back to rule-based insights
    insights = RuleBasedInsightsService.get_business_insights(kpis)
```

### 2. Caching

Cache aggressively to reduce costs:

```python
# Cache for 1 hour for business insights
cache.set(cache_key, insights, 3600)

# Cache for 30 minutes for daily summaries
cache.set(cache_key, summary, 1800)
```

### 3. Monitoring

Track API usage and costs:

```python
import logging

logger = logging.getLogger('claude_insights')

def get_insights(...):
    start_time = time.time()
    try:
        result = client.messages.create(...)
        logger.info(f"Claude API call: {time.time() - start_time:.2f}s")
        return result
    except Exception as e:
        logger.error(f"Claude API failed: {e}")
        raise
```

### 4. Rate Limiting

Implement rate limiting to control costs:

```python
from django_ratelimit.decorators import ratelimit

@ratelimit(key='user', rate='10/h', method='GET')
def get_claude_insights(request):
    # Limited to 10 requests per hour per user
    ...
```

### 5. API Key Security

**Never commit your API key to git!**

```bash
# .gitignore
.env
*.env
config/local_settings.py
```

Store in environment variables:
```bash
# Production (Heroku, AWS, etc.)
heroku config:set ANTHROPIC_API_KEY=sk-ant-...

# Local development
# Use .env file (not committed)
```

---

## Migration Checklist

- [ ] Install anthropic package
- [ ] Get API key from console.anthropic.com
- [ ] Add key to .env file
- [ ] Test with `python analytics/claude_insights.py`
- [ ] Choose integration option (replace/new endpoints/feature flag)
- [ ] Update views to use Claude service
- [ ] Add error handling and fallbacks
- [ ] Test all three insight endpoints
- [ ] Monitor API usage and costs
- [ ] Update documentation

---

## Troubleshooting

### "ModuleNotFoundError: No module named 'anthropic'"

```bash
pip install anthropic>=0.40.0
```

### "Claude API is not available"

Check:
1. Is anthropic installed? `pip list | grep anthropic`
2. Is API key set? `echo $ANTHROPIC_API_KEY`
3. Is key valid? Test at console.anthropic.com

### "AuthenticationError: Invalid API key"

- Check your API key starts with `sk-ant-`
- Verify key at https://console.anthropic.com/settings/keys
- Make sure no extra spaces or quotes in .env file

### "Rate limit exceeded"

- Implement caching (already done in example)
- Add rate limiting to endpoints
- Consider upgrading API plan

### High costs

- Reduce cache timeout (less frequent API calls)
- Use Claude Haiku instead of Sonnet
- Add rate limiting per user
- Batch similar requests

---

## Example: Full Integration

Here's a complete example of integrating Claude into your existing service:

```python
# analytics/ai_insights.py

from analytics.claude_insights import ClaudeInsightsService
import logging

logger = logging.getLogger(__name__)

class AIInsightsService:

    USE_CLAUDE = ClaudeInsightsService.is_available()

    @staticmethod
    def get_business_insights(days: int = 30) -> Dict[str, Any]:
        """Get business insights - Claude or rule-based"""

        # Get base KPI data
        kpis = AnalyticsQueries.get_dashboard_kpis(days=days)

        # Try Claude first if available
        if AIInsightsService.USE_CLAUDE:
            try:
                logger.info("Using Claude for business insights")
                return ClaudeInsightsService.get_business_insights(kpis)
            except Exception as e:
                logger.error(f"Claude API failed, falling back to rules: {e}")

        # Fallback to rule-based
        logger.info("Using rule-based business insights")
        return AIInsightsService._rule_based_insights(kpis)

    @staticmethod
    def _rule_based_insights(kpis: Dict) -> Dict:
        """Original rule-based logic (fallback)"""
        # ... existing implementation ...
```

---

## Need Help?

- **Anthropic Docs**: https://docs.anthropic.com/
- **Support**: support@anthropic.com
- **GitHub Issues**: [Your repo]/issues

---

## Summary

1. ✅ Install: `pip install anthropic`
2. ✅ Get key: https://console.anthropic.com/
3. ✅ Set env: `ANTHROPIC_API_KEY=sk-ant-...`
4. ✅ Test: `python analytics/claude_insights.py`
5. ✅ Integrate: Choose your preferred option
6. ✅ Monitor: Track usage and costs

**Recommended for:**
- Production apps with budget for AI
- Businesses needing deep, contextual insights
- Apps with caching to minimize costs

**Stick with rule-based if:**
- Budget is very limited
- Insights are simple/templated
- Offline operation is required