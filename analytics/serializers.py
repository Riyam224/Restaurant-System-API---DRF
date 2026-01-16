"""
Serializers for analytics API responses.
"""
from rest_framework import serializers


class RevenueMetricsSerializer(serializers.Serializer):
    """Serializer for revenue metrics."""
    total_revenue = serializers.FloatField()
    total_orders = serializers.IntegerField()
    average_order_value = serializers.FloatField()
    total_discount = serializers.FloatField()
    gross_revenue = serializers.FloatField()
    period = serializers.DictField()


class DailyRevenueSerializer(serializers.Serializer):
    """Serializer for daily revenue data."""
    date = serializers.CharField()
    revenue = serializers.FloatField()
    orders = serializers.IntegerField()
    average_order_value = serializers.FloatField()


class OrderStatusSerializer(serializers.Serializer):
    """Serializer for order status breakdown."""
    status = serializers.CharField()
    count = serializers.IntegerField()
    total_value = serializers.FloatField()


class OrderStatusBreakdownSerializer(serializers.Serializer):
    """Serializer for complete order status breakdown."""
    by_status = OrderStatusSerializer(many=True)
    total_orders = serializers.IntegerField()


class TopCustomerSerializer(serializers.Serializer):
    """Serializer for top customer data."""
    user_id = serializers.IntegerField()
    username = serializers.CharField()
    order_count = serializers.IntegerField()
    total_spent = serializers.FloatField()


class UserMetricsSerializer(serializers.Serializer):
    """Serializer for user metrics."""
    total_users = serializers.IntegerField()
    users_with_orders = serializers.IntegerField()
    active_users_30d = serializers.IntegerField()
    conversion_rate = serializers.FloatField()
    top_customers = TopCustomerSerializer(many=True)


class ProductPerformanceSerializer(serializers.Serializer):
    """Serializer for product performance data."""
    product_id = serializers.IntegerField()
    product_name = serializers.CharField()
    total_quantity = serializers.IntegerField()
    total_revenue = serializers.FloatField()
    order_count = serializers.IntegerField()


class CouponStatsSerializer(serializers.Serializer):
    """Serializer for individual coupon statistics."""
    coupon_code = serializers.CharField()
    usage_count = serializers.IntegerField()
    total_discount = serializers.FloatField()
    total_revenue = serializers.FloatField()


class CouponPerformanceSerializer(serializers.Serializer):
    """Serializer for coupon performance metrics."""
    total_discount_given = serializers.FloatField()
    orders_with_coupons = serializers.IntegerField()
    by_coupon = CouponStatsSerializer(many=True)


class RatingDistributionSerializer(serializers.Serializer):
    """Serializer for rating distribution."""
    rating = serializers.IntegerField()
    count = serializers.IntegerField()


class ReviewMetricsSerializer(serializers.Serializer):
    """Serializer for review metrics."""
    total_reviews = serializers.IntegerField()
    average_rating = serializers.FloatField()
    rating_distribution = RatingDistributionSerializer(many=True)


class RevenueDataSerializer(serializers.Serializer):
    """Serializer for revenue data in KPIs."""
    current = serializers.FloatField()
    previous = serializers.FloatField()
    growth_percentage = serializers.FloatField()


class OrderDataSerializer(serializers.Serializer):
    """Serializer for order data in KPIs."""
    current = serializers.IntegerField()
    previous = serializers.IntegerField()
    growth_percentage = serializers.FloatField()


class DashboardKPIsSerializer(serializers.Serializer):
    """Serializer for dashboard KPIs."""
    period_days = serializers.IntegerField()
    revenue = RevenueDataSerializer()
    orders = OrderDataSerializer()
    average_order_value = serializers.FloatField()
    total_users = serializers.IntegerField()
    active_users = serializers.IntegerField()
    conversion_rate = serializers.FloatField()
    order_status = OrderStatusSerializer(many=True)


# AI Insights Serializers (Phase 2)

class DailyMetricsSerializer(serializers.Serializer):
    """Serializer for daily metrics."""
    revenue = serializers.FloatField()
    orders = serializers.IntegerField()
    average_order_value = serializers.FloatField()


class MetricChangesSerializer(serializers.Serializer):
    """Serializer for metric changes."""
    revenue_change = serializers.FloatField()
    revenue_change_percentage = serializers.FloatField()
    order_change = serializers.IntegerField()
    order_change_percentage = serializers.FloatField()


class DailySummarySerializer(serializers.Serializer):
    """Serializer for AI-generated daily summary."""
    date = serializers.CharField()
    summary = serializers.CharField()
    headline = serializers.CharField()
    metrics = DailyMetricsSerializer()
    changes = MetricChangesSerializer()
    insights = serializers.ListField(child=serializers.CharField())


class MetricExplanationSerializer(serializers.Serializer):
    """Serializer for metric change explanation."""
    metric = serializers.CharField()
    trend = serializers.CharField()
    change = serializers.FloatField()
    change_percentage = serializers.FloatField()
    explanation = serializers.CharField()
    contributing_factors = serializers.ListField(child=serializers.CharField())
    current_value = serializers.FloatField()
    previous_value = serializers.FloatField()


class BusinessInsightsSerializer(serializers.Serializer):
    """Serializer for comprehensive business insights."""
    period = serializers.CharField()
    overview = serializers.CharField()
    opportunities = serializers.ListField(child=serializers.CharField())
    warnings = serializers.ListField(child=serializers.CharField())
    recommendations = serializers.ListField(child=serializers.CharField())
    kpis = DashboardKPIsSerializer()
