"""
AI-powered insights layer for analytics.

Generates natural language explanations and summaries of analytics data.
Uses Claude API (Anthropic) for intelligent business insights.
"""
import os
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from django.utils import timezone
from django.core.cache import cache

from .queries import AnalyticsQueries


class AIInsightsService:
    """
    Service for generating AI-powered insights from analytics data.

    This uses simple rule-based logic for Phase 2. Can be upgraded to
    use Claude API or other LLMs for more sophisticated insights.
    """

    @staticmethod
    def generate_daily_summary(date: Optional[datetime] = None) -> Dict[str, Any]:
        """
        Generate a "What happened today?" summary.

        Args:
            date: Date to summarize (defaults to today)

        Returns:
            dict: Natural language summary of the day's performance
        """
        if not date:
            date = timezone.now()

        # Get data for today
        start_of_day = date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = date.replace(hour=23, minute=59, second=59, microsecond=999999)

        today_metrics = AnalyticsQueries.get_revenue_metrics(start_of_day, end_of_day)

        # Get yesterday's data for comparison
        yesterday_start = start_of_day - timedelta(days=1)
        yesterday_end = end_of_day - timedelta(days=1)
        yesterday_metrics = AnalyticsQueries.get_revenue_metrics(yesterday_start, yesterday_end)

        # Calculate changes
        revenue_change = today_metrics['total_revenue'] - yesterday_metrics['total_revenue']
        revenue_change_pct = (
            (revenue_change / yesterday_metrics['total_revenue'] * 100)
            if yesterday_metrics['total_revenue'] > 0 else 100.0
        )

        order_change = today_metrics['total_orders'] - yesterday_metrics['total_orders']
        order_change_pct = (
            (order_change / yesterday_metrics['total_orders'] * 100)
            if yesterday_metrics['total_orders'] > 0 else 100.0
        )

        # Generate natural language summary
        summary = AIInsightsService._create_daily_narrative(
            today_metrics,
            yesterday_metrics,
            revenue_change_pct,
            order_change_pct
        )

        # Get contributing factors
        factors = AIInsightsService._analyze_contributing_factors(
            start_of_day, end_of_day
        )

        return {
            'date': date.date().isoformat(),
            'summary': summary,
            'headline': AIInsightsService._create_headline(revenue_change_pct, order_change_pct),
            'metrics': {
                'revenue': today_metrics['total_revenue'],
                'orders': today_metrics['total_orders'],
                'average_order_value': today_metrics['average_order_value']
            },
            'changes': {
                'revenue_change': revenue_change,
                'revenue_change_percentage': round(revenue_change_pct, 1),
                'order_change': order_change,
                'order_change_percentage': round(order_change_pct, 1)
            },
            'insights': factors
        }

    @staticmethod
    def _create_headline(revenue_change_pct: float, order_change_pct: float) -> str:
        """Create a headline for the daily summary."""
        if revenue_change_pct > 20:
            return "🚀 Strong Performance Today!"
        elif revenue_change_pct > 10:
            return "📈 Growth Continues"
        elif revenue_change_pct > 0:
            return "✅ Steady Progress"
        elif revenue_change_pct > -10:
            return "📊 Slight Dip Today"
        else:
            return "⚠️ Needs Attention"

    @staticmethod
    def _create_daily_narrative(
        today: Dict,
        yesterday: Dict,
        revenue_change_pct: float,
        order_change_pct: float
    ) -> str:
        """Create natural language narrative of the day."""
        parts = []

        # Revenue narrative
        if revenue_change_pct > 0:
            parts.append(
                f"Revenue increased by {abs(revenue_change_pct):.1f}% "
                f"to ${today['total_revenue']:.2f}"
            )
        elif revenue_change_pct < 0:
            parts.append(
                f"Revenue decreased by {abs(revenue_change_pct):.1f}% "
                f"to ${today['total_revenue']:.2f}"
            )
        else:
            parts.append(f"Revenue held steady at ${today['total_revenue']:.2f}")

        # Order volume narrative
        if order_change_pct > 0:
            parts.append(
                f"with {today['total_orders']} orders "
                f"(up {abs(order_change_pct):.1f}%)"
            )
        elif order_change_pct < 0:
            parts.append(
                f"with {today['total_orders']} orders "
                f"(down {abs(order_change_pct):.1f}%)"
            )
        else:
            parts.append(f"with {today['total_orders']} orders")

        # Average order value
        aov_change = today['average_order_value'] - yesterday['average_order_value']
        if abs(aov_change) > 1:
            if aov_change > 0:
                parts.append(
                    f"Average order value increased to ${today['average_order_value']:.2f}"
                )
            else:
                parts.append(
                    f"Average order value decreased to ${today['average_order_value']:.2f}"
                )

        return ". ".join(parts) + "."

    @staticmethod
    def _analyze_contributing_factors(start_date: datetime, end_date: datetime) -> List[str]:
        """Analyze what contributed to today's performance."""
        insights = []

        # Check coupon usage
        coupon_perf = AnalyticsQueries.get_coupon_performance()
        if coupon_perf['orders_with_coupons'] > 0:
            insights.append(
                f"Coupons drove {coupon_perf['orders_with_coupons']} orders, "
                f"with ${coupon_perf['total_discount_given']:.2f} in discounts"
            )

        # Check product performance
        products = AnalyticsQueries.get_product_performance()
        if products:
            top_product = products[0]
            insights.append(
                f"Top seller: {top_product['product_name']} "
                f"({top_product['order_count']} orders)"
            )

        # Check order status
        status = AnalyticsQueries.get_order_status_breakdown()
        if status['by_status']:
            pending_orders = sum(
                s['count'] for s in status['by_status']
                if s['status'] in ['pending', 'preparing']
            )
            if pending_orders > 0:
                insights.append(f"{pending_orders} orders currently being processed")

        return insights

    @staticmethod
    def explain_metric_change(
        metric_name: str,
        current_value: float,
        previous_value: float,
        period_days: int = 30
    ) -> Dict[str, Any]:
        """
        Explain why a metric changed.

        Args:
            metric_name: Name of the metric (revenue, orders, etc.)
            current_value: Current period value
            previous_value: Previous period value
            period_days: Number of days in the period

        Returns:
            dict: Natural language explanation of the change
        """
        change = current_value - previous_value
        change_pct = (
            (change / previous_value * 100)
            if previous_value > 0 else 100.0
        )

        # Determine trend
        if abs(change_pct) < 5:
            trend = "stable"
        elif change_pct > 0:
            trend = "increasing"
        else:
            trend = "decreasing"

        # Generate explanation
        explanation = AIInsightsService._generate_change_explanation(
            metric_name, trend, change_pct, period_days
        )

        # Get contributing factors
        factors = AIInsightsService._get_change_factors(metric_name, trend)

        return {
            'metric': metric_name,
            'trend': trend,
            'change': change,
            'change_percentage': round(change_pct, 1),
            'explanation': explanation,
            'contributing_factors': factors,
            'current_value': current_value,
            'previous_value': previous_value
        }

    @staticmethod
    def _generate_change_explanation(
        metric: str,
        trend: str,
        change_pct: float,
        days: int
    ) -> str:
        """Generate natural language explanation for metric change."""
        if trend == "stable":
            return (
                f"{metric.capitalize()} has remained relatively stable "
                f"over the past {days} days, showing consistent performance."
            )
        elif trend == "increasing":
            if change_pct > 50:
                intensity = "significantly increased"
            elif change_pct > 20:
                intensity = "increased substantially"
            else:
                intensity = "increased"

            return (
                f"{metric.capitalize()} has {intensity} by {abs(change_pct):.1f}% "
                f"compared to the previous {days}-day period."
            )
        else:  # decreasing
            if change_pct < -50:
                intensity = "dropped significantly"
            elif change_pct < -20:
                intensity = "decreased substantially"
            else:
                intensity = "decreased"

            return (
                f"{metric.capitalize()} has {intensity} by {abs(change_pct):.1f}% "
                f"compared to the previous {days}-day period."
            )

    @staticmethod
    def _get_change_factors(metric: str, trend: str) -> List[str]:
        """Get potential factors contributing to metric change."""
        factors = []

        # Get current data
        user_metrics = AnalyticsQueries.get_user_metrics()
        coupon_perf = AnalyticsQueries.get_coupon_performance()

        if metric == "revenue":
            if trend == "increasing":
                factors.append("Higher order volume")
                if coupon_perf['orders_with_coupons'] > 0:
                    factors.append("Successful coupon campaigns")
                if user_metrics['active_users_30d'] > user_metrics['total_users'] * 0.3:
                    factors.append("Strong user engagement")
            else:
                factors.append("Lower order volume")
                if coupon_perf['total_discount_given'] > 0:
                    factors.append("Increased discount usage")

        elif metric == "orders":
            if trend == "increasing":
                factors.append("Growing customer base")
                if user_metrics['conversion_rate'] > 50:
                    factors.append("High conversion rate")
            else:
                factors.append("Reduced customer activity")

        return factors

    @staticmethod
    def get_business_insights(days: int = 30) -> Dict[str, Any]:
        """
        Get comprehensive business insights for a period.

        Args:
            days: Number of days to analyze

        Returns:
            dict: Business insights in natural language
        """
        # Check cache first
        cache_key = f'ai_insights_business_{days}'
        cached = cache.get(cache_key)
        if cached:
            return cached

        # Get dashboard KPIs
        kpis = AnalyticsQueries.get_dashboard_kpis(days=days)

        # Generate insights
        insights = {
            'period': f"Last {days} days",
            'overview': AIInsightsService._create_business_overview(kpis),
            'opportunities': AIInsightsService._identify_opportunities(kpis),
            'warnings': AIInsightsService._identify_warnings(kpis),
            'recommendations': AIInsightsService._generate_recommendations(kpis),
            'kpis': kpis
        }

        # Cache for 1 hour
        cache.set(cache_key, insights, 3600)

        return insights

    @staticmethod
    def _create_business_overview(kpis: Dict) -> str:
        """Create business overview from KPIs."""
        revenue_trend = "up" if kpis['revenue']['growth_percentage'] > 0 else "down"

        return (
            f"Over the past {kpis['period_days']} days, revenue is {revenue_trend} "
            f"{abs(kpis['revenue']['growth_percentage']):.1f}% to "
            f"${kpis['revenue']['current']:.2f} with "
            f"{kpis['orders']['current']} orders. "
            f"You have {kpis['total_users']} total users with "
            f"{kpis['active_users']} active in this period "
            f"({kpis['conversion_rate']:.1f}% conversion rate)."
        )

    @staticmethod
    def _identify_opportunities(kpis: Dict) -> List[str]:
        """Identify business opportunities from KPIs."""
        opportunities = []

        if kpis['revenue']['growth_percentage'] > 20:
            opportunities.append(
                "Strong growth momentum - consider expanding marketing efforts"
            )

        if kpis['conversion_rate'] < 50:
            opportunities.append(
                "Conversion rate could be improved - focus on user engagement"
            )

        if kpis['average_order_value'] < 20:
            opportunities.append(
                "Low average order value - consider upselling strategies"
            )

        return opportunities

    @staticmethod
    def _identify_warnings(kpis: Dict) -> List[str]:
        """Identify potential issues from KPIs."""
        warnings = []

        if kpis['revenue']['growth_percentage'] < -20:
            warnings.append("Significant revenue decline - investigate causes")

        if kpis['orders']['growth_percentage'] < -10:
            warnings.append("Order volume decreasing - review customer satisfaction")

        if kpis['active_users'] < kpis['total_users'] * 0.2:
            warnings.append("Low user engagement - consider re-engagement campaigns")

        return warnings

    @staticmethod
    def _generate_recommendations(kpis: Dict) -> List[str]:
        """Generate actionable recommendations."""
        recommendations = []

        # Revenue recommendations
        if kpis['revenue']['growth_percentage'] < 0:
            recommendations.append(
                "Run promotional campaigns to boost revenue"
            )

        # Order recommendations
        if kpis['orders']['growth_percentage'] < 5:
            recommendations.append(
                "Introduce limited-time offers to drive order volume"
            )

        # User engagement recommendations
        if kpis['conversion_rate'] < 40:
            recommendations.append(
                "Improve user onboarding and first-time purchase incentives"
            )

        # AOV recommendations
        if kpis['average_order_value'] < 25:
            recommendations.append(
                "Implement combo deals or minimum order promotions"
            )

        return recommendations if recommendations else [
            "Performance is strong - maintain current strategies"
        ]
