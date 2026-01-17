"""
AI-Powered Anomaly Explainer

Generates natural language explanations for detected anomalies using:
1. Rule-based logic (fast, free)
2. Claude API (optional, more detailed)

Provides context-aware explanations that help understand WHY anomalies occurred.
"""

import json
from typing import Dict, Any, List
from django.core.cache import cache

try:
    import anthropic
    from analytics.claude_insights import ClaudeInsightsService
    CLAUDE_AVAILABLE = ClaudeInsightsService.is_available()
except ImportError:
    CLAUDE_AVAILABLE = False


class AnomalyExplainer:
    """
    Generate human-readable explanations for detected anomalies.

    Supports both rule-based (free) and Claude-powered (paid) explanations.
    """

    @staticmethod
    def explain_anomaly(anomaly: Dict[str, Any], use_ai: bool = False) -> str:
        """
        Generate a natural language explanation for an anomaly.

        Args:
            anomaly: Anomaly dictionary from AnomalyDetector
            use_ai: Whether to use Claude API (if available)

        Returns:
            Natural language explanation string
        """
        if use_ai and CLAUDE_AVAILABLE:
            try:
                return AnomalyExplainer._explain_with_claude(anomaly)
            except Exception:
                pass  # Fallback to rule-based

        return AnomalyExplainer._explain_with_rules(anomaly)

    @staticmethod
    def explain_all_anomalies(
        anomalies: List[Dict[str, Any]],
        use_ai: bool = False
    ) -> Dict[str, Any]:
        """
        Generate explanations for a list of anomalies.

        Returns a summary with overall pattern analysis.
        """
        if not anomalies:
            return {
                'summary': 'No anomalies detected. Operations appear normal.',
                'anomalies': [],
                'pattern_analysis': 'All metrics are within expected ranges.',
                'recommended_actions': []
            }

        # Explain each anomaly
        explained_anomalies = []
        for anomaly in anomalies:
            explained = anomaly.copy()
            explained['ai_explanation'] = AnomalyExplainer.explain_anomaly(
                anomaly,
                use_ai=use_ai
            )
            explained_anomalies.append(explained)

        # Generate overall summary
        if use_ai and CLAUDE_AVAILABLE:
            try:
                summary = AnomalyExplainer._generate_summary_with_claude(explained_anomalies)
            except Exception:
                summary = AnomalyExplainer._generate_summary_with_rules(explained_anomalies)
        else:
            summary = AnomalyExplainer._generate_summary_with_rules(explained_anomalies)

        return {
            **summary,
            'anomalies': explained_anomalies
        }

    @staticmethod
    def _explain_with_rules(anomaly: Dict[str, Any]) -> str:
        """Generate rule-based explanation (free, fast)."""
        anomaly_type = anomaly.get('type', '')

        # Revenue spike
        if anomaly_type == 'revenue_spike':
            explanation = f"Revenue spiked to ${anomaly['value']:.2f} on {anomaly['date']}, which is {anomaly['change_percentage']:.0f}% above normal. "

            reasons = anomaly.get('possible_reasons', [])
            if reasons:
                explanation += f"Likely due to: {', '.join(reasons[:2])}."

            return explanation

        # Revenue drop
        elif anomaly_type == 'revenue_drop':
            explanation = f"Revenue dropped to ${anomaly['value']:.2f} on {anomaly['date']}, {abs(anomaly['change_percentage']):.0f}% below the usual ${anomaly['baseline']:.2f}. "

            reasons = anomaly.get('possible_reasons', [])
            if reasons:
                explanation += f"Possible causes: {', '.join(reasons[:2])}."

            return explanation

        # Order spike
        elif anomaly_type == 'order_spike':
            return f"Order volume surged to {anomaly['value']} orders on {anomaly['date']}, significantly higher than the normal {anomaly['baseline']:.0f} orders per day."

        # Order drop
        elif anomaly_type == 'order_drop':
            return f"Only {anomaly['value']} orders received on {anomaly['date']}, well below the typical {anomaly['baseline']:.0f} orders. This may indicate a service issue or external factors affecting demand."

        # Coupon abuse
        elif 'coupon_abuse' in anomaly_type:
            if anomaly_type == 'coupon_abuse_heavy_usage':
                return f"User '{anomaly['username']}' has used coupons {anomaly['value']} times, exceeding normal usage patterns. Review for potential account sharing or abuse."
            elif anomaly_type == 'coupon_abuse_high_discount':
                return f"Order #{anomaly['order_id']} received an unusually high {anomaly['value']:.0f}% discount. Check if coupon stacking or system errors are allowing excessive discounts."

        # User anomalies
        elif 'user' in anomaly_type:
            if anomaly_type == 'user_spike':
                return f"{anomaly['value']} new users registered recently, {anomaly['change_ratio']:.1f}x the normal rate. Verify these are legitimate registrations and not bot activity."
            elif anomaly_type == 'high_frequency_ordering':
                return f"User '{anomaly['username']}' has placed {anomaly['value']} orders recently. This could be a business customer or catering orders - consider VIP treatment."

        # Default
        return f"{anomaly.get('title', 'Anomaly detected')}: {anomaly.get('description', 'Unusual pattern detected.')}"

    @staticmethod
    def _explain_with_claude(anomaly: Dict[str, Any]) -> str:
        """Generate AI-powered explanation using Claude (requires API key)."""
        cache_key = f"anomaly_explain_{anomaly['type']}_{anomaly.get('date', 'today')}"
        cached = cache.get(cache_key)
        if cached:
            return cached

        prompt = f"""Explain this restaurant operations anomaly in 2-3 clear sentences:

Type: {anomaly['type']}
Date: {anomaly.get('date', 'today')}
Description: {anomaly.get('description', '')}
Value: {anomaly.get('value', 'N/A')}
Baseline: {anomaly.get('baseline', 'N/A')}
Possible Reasons: {', '.join(anomaly.get('possible_reasons', []))}

Provide:
1. What happened (factual)
2. Why it likely happened (most probable reason)
3. What to do about it (actionable advice)

Be specific and concise. Use plain language for restaurant managers."""

        try:
            client = anthropic.Anthropic(api_key=ClaudeInsightsService.API_KEY)

            message = client.messages.create(
                model=ClaudeInsightsService.MODEL,
                max_tokens=200,
                temperature=0.7,
                messages=[{"role": "user", "content": prompt}]
            )

            explanation = message.content[0].text.strip()

            # Cache for 30 minutes
            cache.set(cache_key, explanation, 1800)

            return explanation

        except Exception as e:
            # Fallback to rule-based
            return AnomalyExplainer._explain_with_rules(anomaly)

    @staticmethod
    def _generate_summary_with_rules(anomalies: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate overall summary using rules."""
        critical = [a for a in anomalies if a['severity'] == 'critical']
        warnings = [a for a in anomalies if a['severity'] == 'warning']

        if critical:
            summary = f"⚠️ {len(critical)} critical issue(s) detected requiring immediate attention. "
        elif warnings:
            summary = f"⚡ {len(warnings)} warning(s) detected. Review recommended. "
        else:
            summary = f"ℹ️ {len(anomalies)} unusual pattern(s) detected. Monitoring suggested. "

        # Pattern analysis
        types = [a['type'] for a in anomalies]
        if types.count('revenue_drop') > 2:
            pattern = "Multiple revenue drops suggest a broader demand issue."
        elif types.count('coupon_abuse_heavy_usage') > 0:
            pattern = "Coupon usage patterns indicate potential abuse or gaming."
        elif 'user_spike' in types:
            pattern = "Unusual user growth - verify registration legitimacy."
        else:
            pattern = "Various operational anomalies detected across metrics."

        # Recommended actions
        actions = []
        if critical:
            actions.append("Investigate critical issues immediately")
        if any('coupon' in a['type'] for a in anomalies):
            actions.append("Review coupon policies and usage limits")
        if any('revenue_drop' in a['type'] for a in anomalies):
            actions.append("Analyze drop causes and address service issues")
        if any('order_drop' in a['type'] for a in anomalies):
            actions.append("Check for technical problems or delivery issues")

        return {
            'summary': summary,
            'pattern_analysis': pattern,
            'recommended_actions': actions or ['Monitor trends and investigate further']
        }

    @staticmethod
    def _generate_summary_with_claude(anomalies: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate AI-powered overall summary."""
        # Prepare anomaly summary for Claude
        anomaly_summary = []
        for a in anomalies[:5]:  # Top 5 most important
            anomaly_summary.append({
                'type': a['type'],
                'severity': a['severity'],
                'description': a.get('description', '')
            })

        prompt = f"""Analyze these restaurant operation anomalies and provide strategic insights:

Detected Anomalies:
{json.dumps(anomaly_summary, indent=2)}

Total Anomalies: {len(anomalies)}

Provide in JSON format:
{{
    "summary": "2-sentence overview of the situation",
    "pattern_analysis": "1-2 sentences about overall patterns or trends",
    "recommended_actions": ["action 1", "action 2", "action 3"]
}}

Focus on actionable insights for restaurant managers."""

        try:
            client = anthropic.Anthropic(api_key=ClaudeInsightsService.API_KEY)

            message = client.messages.create(
                model=ClaudeInsightsService.MODEL,
                max_tokens=400,
                temperature=0.7,
                messages=[{"role": "user", "content": prompt}]
            )

            result = json.loads(message.content[0].text)
            return result

        except Exception:
            # Fallback to rule-based
            return AnomalyExplainer._generate_summary_with_rules(anomalies)


# Template for daily anomaly digest
def generate_daily_digest(anomalies: List[Dict[str, Any]]) -> str:
    """
    Generate a daily digest email/notification text.

    Args:
        anomalies: List of detected anomalies

    Returns:
        Formatted digest text
    """
    if not anomalies:
        return "✅ No anomalies detected today. Operations are normal."

    critical = [a for a in anomalies if a['severity'] == 'critical']
    warnings = [a for a in anomalies if a['severity'] == 'warning']
    info = [a for a in anomalies if a['severity'] == 'info']

    digest = "🔔 Daily Anomaly Report\n\n"

    if critical:
        digest += f"🚨 CRITICAL ({len(critical)}):\n"
        for a in critical:
            digest += f"  • {a['title']}\n"
            digest += f"    {AnomalyExplainer.explain_anomaly(a)}\n\n"

    if warnings:
        digest += f"⚠️ WARNINGS ({len(warnings)}):\n"
        for a in warnings:
            digest += f"  • {a['title']}\n"
            digest += f"    {AnomalyExplainer.explain_anomaly(a)}\n\n"

    if info and not (critical or warnings):
        digest += f"ℹ️ INFO ({len(info)}):\n"
        for a in info[:3]:  # Top 3 info items
            digest += f"  • {a['title']}\n"

    return digest