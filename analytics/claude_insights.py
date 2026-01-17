"""
Claude-powered AI Insights Service

This module provides AI-generated insights using Anthropic's Claude API.
It replaces rule-based logic with actual AI analysis of business data.

Setup:
1. Install: pip install anthropic
2. Set environment variable: ANTHROPIC_API_KEY=your-key-here
3. Update settings.py or .env file with your API key

Usage:
    from analytics.claude_insights import ClaudeInsightsService

    insights = ClaudeInsightsService.get_business_insights(kpis_data)
"""

import os
import json
from typing import Dict, List, Any, Optional
from django.conf import settings
from django.core.cache import cache

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False


class ClaudeInsightsService:
    """
    Generate AI insights using Claude API.

    This service analyzes restaurant business data and generates:
    - Natural language summaries
    - Trend explanations
    - Actionable recommendations
    - Business opportunities and warnings
    """

    # Get API key from settings or environment
    API_KEY = getattr(settings, 'ANTHROPIC_API_KEY', os.getenv('ANTHROPIC_API_KEY'))

    # Default model to use
    MODEL = "claude-sonnet-4-5-20250929"

    @classmethod
    def is_available(cls) -> bool:
        """Check if Claude API is available and configured."""
        return ANTHROPIC_AVAILABLE and bool(cls.API_KEY)

    @classmethod
    def get_daily_summary(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a natural language summary of daily performance.

        Args:
            data: Dictionary containing today's metrics (revenue, orders, etc.)

        Returns:
            Dictionary with headline, summary, and insights
        """
        if not cls.is_available():
            raise ValueError(
                "Claude API is not available. "
                "Install anthropic package and set ANTHROPIC_API_KEY."
            )

        # Check cache
        cache_key = f"claude_daily_{data.get('date', 'today')}"
        cached = cache.get(cache_key)
        if cached:
            return cached

        # Prepare prompt
        prompt = f"""Analyze this restaurant's daily performance and create a concise summary:

Today's Data:
- Revenue: ${data.get('revenue', 0):.2f} (previous: ${data.get('previous_revenue', 0):.2f})
- Orders: {data.get('orders', 0)} (previous: {data.get('previous_orders', 0)})
- Average Order Value: ${data.get('average_order_value', 0):.2f}
- Coupons Used: {data.get('coupon_orders', 0)} orders with ${data.get('discount_amount', 0):.2f} in discounts
- Top Product: {data.get('top_product', 'N/A')} ({data.get('top_product_orders', 0)} orders)
- Pending Orders: {data.get('pending_orders', 0)}

Provide:
1. A short headline (under 40 chars, use emoji like 📈 🚀 ⚠️)
2. A 2-sentence summary of overall performance
3. 2-3 key insights (actionable observations)

Format as JSON:
{{
    "headline": "...",
    "summary": "...",
    "insights": ["...", "..."]
}}"""

        try:
            client = anthropic.Anthropic(api_key=cls.API_KEY)

            message = client.messages.create(
                model=cls.MODEL,
                max_tokens=500,
                temperature=0.7,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )

            # Parse response
            response_text = message.content[0].text
            result = json.loads(response_text)

            # Cache for 30 minutes
            cache.set(cache_key, result, 1800)

            return result

        except Exception as e:
            # Fallback to simple response if API fails
            return {
                "headline": "📊 Daily Summary",
                "summary": f"Revenue: ${data.get('revenue', 0):.2f}, Orders: {data.get('orders', 0)}",
                "insights": [f"Claude API error: {str(e)}"]
            }

    @classmethod
    def explain_metric_change(
        cls,
        metric_name: str,
        current_value: float,
        previous_value: float,
        additional_context: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Generate an AI explanation for why a metric changed.

        Args:
            metric_name: Name of the metric (revenue, orders, users)
            current_value: Current period value
            previous_value: Previous period value
            additional_context: Optional dict with extra data

        Returns:
            Dictionary with explanation, trend, and contributing factors
        """
        if not cls.is_available():
            raise ValueError("Claude API is not available.")

        change = current_value - previous_value
        change_pct = ((change / previous_value * 100) if previous_value > 0 else 100.0)

        context = additional_context or {}

        prompt = f"""Analyze this restaurant metric change:

Metric: {metric_name}
Current Value: {current_value}
Previous Value: {previous_value}
Change: {change:+.2f} ({change_pct:+.1f}%)

Additional Context:
{json.dumps(context, indent=2)}

Provide:
1. Trend: "increasing", "decreasing", or "stable"
2. A 2-sentence explanation of WHY this happened
3. 2-4 contributing factors (specific, actionable)

Format as JSON:
{{
    "trend": "...",
    "explanation": "...",
    "contributing_factors": ["...", "..."]
}}"""

        try:
            client = anthropic.Anthropic(api_key=cls.API_KEY)

            message = client.messages.create(
                model=cls.MODEL,
                max_tokens=600,
                temperature=0.7,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )

            response_text = message.content[0].text
            result = json.loads(response_text)

            return {
                'metric': metric_name,
                'trend': result['trend'],
                'change': change,
                'change_percentage': round(change_pct, 1),
                'explanation': result['explanation'],
                'contributing_factors': result['contributing_factors'],
                'current_value': current_value,
                'previous_value': previous_value
            }

        except Exception as e:
            return {
                'metric': metric_name,
                'trend': 'unknown',
                'change': change,
                'change_percentage': round(change_pct, 1),
                'explanation': f"Unable to generate explanation: {str(e)}",
                'contributing_factors': [],
                'current_value': current_value,
                'previous_value': previous_value
            }

    @classmethod
    def get_business_insights(cls, kpis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate comprehensive business insights from KPIs.

        Args:
            kpis: Dictionary containing all business KPIs

        Returns:
            Dictionary with overview, opportunities, warnings, and recommendations
        """
        if not cls.is_available():
            raise ValueError("Claude API is not available.")

        # Check cache
        cache_key = f"claude_business_{kpis.get('period_days', 30)}"
        cached = cache.get(cache_key)
        if cached:
            return cached

        prompt = f"""Analyze this restaurant's business performance and provide strategic insights:

Business KPIs ({kpis.get('period_days', 30)} days):

Revenue:
- Current: ${kpis['revenue']['current']:.2f}
- Previous: ${kpis['revenue']['previous']:.2f}
- Growth: {kpis['revenue']['growth_percentage']:.1f}%

Orders:
- Current: {kpis['orders']['current']}
- Previous: {kpis['orders']['previous']}
- Growth: {kpis['orders']['growth_percentage']:.1f}%

Customer Metrics:
- Total Users: {kpis.get('total_users', 0)}
- Active Users: {kpis.get('active_users', 0)}
- Conversion Rate: {kpis.get('conversion_rate', 0):.1f}%
- Average Order Value: ${kpis.get('average_order_value', 0):.2f}

Order Status:
{json.dumps(kpis.get('order_status', []), indent=2)}

Provide:
1. A 2-3 sentence business overview
2. 2-3 opportunities (growth potential, market gaps)
3. 1-2 warnings (concerns, risks to address)
4. 3-4 actionable recommendations (specific, prioritized)

Format as JSON:
{{
    "overview": "...",
    "opportunities": ["...", "..."],
    "warnings": ["...", "..."],
    "recommendations": ["...", "...", "..."]
}}"""

        try:
            client = anthropic.Anthropic(api_key=cls.API_KEY)

            message = client.messages.create(
                model=cls.MODEL,
                max_tokens=800,
                temperature=0.7,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )

            response_text = message.content[0].text
            result = json.loads(response_text)

            # Add KPIs to response
            result['period'] = f"Last {kpis.get('period_days', 30)} days"
            result['kpis'] = kpis

            # Cache for 1 hour
            cache.set(cache_key, result, 3600)

            return result

        except Exception as e:
            return {
                'period': f"Last {kpis.get('period_days', 30)} days",
                'overview': f"Unable to generate insights: {str(e)}",
                'opportunities': [],
                'warnings': [],
                'recommendations': [],
                'kpis': kpis
            }


# Example usage and testing
if __name__ == "__main__":
    # Example test data
    test_kpis = {
        'period_days': 30,
        'revenue': {'current': 1636.92, 'previous': 0.0, 'growth_percentage': 100.0},
        'orders': {'current': 54, 'previous': 0, 'growth_percentage': 100.0},
        'average_order_value': 30.31,
        'total_users': 7,
        'active_users': 3,
        'conversion_rate': 42.86,
        'order_status': [
            {'status': 'delivered', 'count': 54, 'total_value': 1636.92},
            {'status': 'preparing', 'count': 18, 'total_value': 293.64}
        ]
    }

    if ClaudeInsightsService.is_available():
        print("✅ Claude API is available")
        print("\nTesting business insights...")
        insights = ClaudeInsightsService.get_business_insights(test_kpis)
        print(json.dumps(insights, indent=2))
    else:
        print("❌ Claude API is not available")
        print("Set ANTHROPIC_API_KEY environment variable to enable")