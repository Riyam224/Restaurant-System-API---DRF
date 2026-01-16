"""
Analytics API views - Admin only, read-only endpoints.
"""
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from datetime import datetime, timedelta
from django.utils import timezone

from .queries import AnalyticsQueries
from .permissions import IsAdminUser
from .ai_insights import AIInsightsService
from .serializers import (
    RevenueMetricsSerializer,
    DailyRevenueSerializer,
    OrderStatusBreakdownSerializer,
    UserMetricsSerializer,
    ProductPerformanceSerializer,
    CouponPerformanceSerializer,
    ReviewMetricsSerializer,
    DashboardKPIsSerializer,
    # AI Insights serializers
    DailySummarySerializer,
    MetricExplanationSerializer,
    BusinessInsightsSerializer,
)


class DashboardKPIsView(APIView):
    """
    Get comprehensive dashboard KPIs.

    Returns key performance indicators including revenue, orders,
    users, and growth metrics.
    """
    permission_classes = [IsAuthenticated, IsAdminUser]

    @extend_schema(
        summary="Get Dashboard KPIs",
        description="Retrieve comprehensive KPIs for the analytics dashboard. Admin only.",
        parameters=[
            OpenApiParameter(
                name='days',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description='Number of days to look back (default: 30)',
                required=False
            )
        ],
        responses={200: DashboardKPIsSerializer},
        tags=['Analytics']
    )
    def get(self, request):
        days = int(request.query_params.get('days', 30))

        # Validate days parameter
        if days < 1 or days > 365:
            return Response(
                {'error': 'Days must be between 1 and 365'},
                status=status.HTTP_400_BAD_REQUEST
            )

        data = AnalyticsQueries.get_dashboard_kpis(days=days)
        serializer = DashboardKPIsSerializer(data)
        return Response(serializer.data)


class RevenueMetricsView(APIView):
    """
    Get revenue metrics for a date range.
    """
    permission_classes = [IsAuthenticated, IsAdminUser]

    @extend_schema(
        summary="Get Revenue Metrics",
        description="Retrieve revenue metrics including total revenue, orders, and averages. Admin only.",
        parameters=[
            OpenApiParameter(
                name='start_date',
                type=OpenApiTypes.DATE,
                location=OpenApiParameter.QUERY,
                description='Start date (YYYY-MM-DD). Default: 30 days ago',
                required=False
            ),
            OpenApiParameter(
                name='end_date',
                type=OpenApiTypes.DATE,
                location=OpenApiParameter.QUERY,
                description='End date (YYYY-MM-DD). Default: today',
                required=False
            )
        ],
        responses={200: RevenueMetricsSerializer},
        tags=['Analytics']
    )
    def get(self, request):
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')

        # Parse dates if provided
        try:
            if start_date:
                start_date = timezone.make_aware(
                    datetime.strptime(start_date, '%Y-%m-%d')
                )
            if end_date:
                end_date = timezone.make_aware(
                    datetime.strptime(end_date, '%Y-%m-%d')
                )
        except ValueError:
            return Response(
                {'error': 'Invalid date format. Use YYYY-MM-DD'},
                status=status.HTTP_400_BAD_REQUEST
            )

        data = AnalyticsQueries.get_revenue_metrics(start_date, end_date)
        serializer = RevenueMetricsSerializer(data)
        return Response(serializer.data)


class DailyRevenueView(APIView):
    """
    Get daily revenue breakdown.
    """
    permission_classes = [IsAuthenticated, IsAdminUser]

    @extend_schema(
        summary="Get Daily Revenue",
        description="Retrieve daily revenue breakdown for charting. Admin only.",
        parameters=[
            OpenApiParameter(
                name='start_date',
                type=OpenApiTypes.DATE,
                location=OpenApiParameter.QUERY,
                description='Start date (YYYY-MM-DD). Default: 30 days ago',
                required=False
            ),
            OpenApiParameter(
                name='end_date',
                type=OpenApiTypes.DATE,
                location=OpenApiParameter.QUERY,
                description='End date (YYYY-MM-DD). Default: today',
                required=False
            )
        ],
        responses={200: DailyRevenueSerializer(many=True)},
        tags=['Analytics']
    )
    def get(self, request):
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')

        # Parse dates if provided
        try:
            if start_date:
                start_date = timezone.make_aware(
                    datetime.strptime(start_date, '%Y-%m-%d')
                )
            if end_date:
                end_date = timezone.make_aware(
                    datetime.strptime(end_date, '%Y-%m-%d')
                )
        except ValueError:
            return Response(
                {'error': 'Invalid date format. Use YYYY-MM-DD'},
                status=status.HTTP_400_BAD_REQUEST
            )

        data = AnalyticsQueries.get_revenue_by_day(start_date, end_date)
        serializer = DailyRevenueSerializer(data, many=True)
        return Response(serializer.data)


class OrderStatusView(APIView):
    """
    Get order status breakdown.
    """
    permission_classes = [IsAuthenticated, IsAdminUser]

    @extend_schema(
        summary="Get Order Status Breakdown",
        description="Retrieve order counts by status. Admin only.",
        responses={200: OrderStatusBreakdownSerializer},
        tags=['Analytics']
    )
    def get(self, request):
        data = AnalyticsQueries.get_order_status_breakdown()
        serializer = OrderStatusBreakdownSerializer(data)
        return Response(serializer.data)


class UserMetricsView(APIView):
    """
    Get user metrics and top customers.
    """
    permission_classes = [IsAuthenticated, IsAdminUser]

    @extend_schema(
        summary="Get User Metrics",
        description="Retrieve user statistics and top customers. Admin only.",
        responses={200: UserMetricsSerializer},
        tags=['Analytics']
    )
    def get(self, request):
        data = AnalyticsQueries.get_user_metrics()
        serializer = UserMetricsSerializer(data)
        return Response(serializer.data)


class ProductPerformanceView(APIView):
    """
    Get product sales performance.
    """
    permission_classes = [IsAuthenticated, IsAdminUser]

    @extend_schema(
        summary="Get Product Performance",
        description="Retrieve top selling products and their metrics. Admin only.",
        responses={200: ProductPerformanceSerializer(many=True)},
        tags=['Analytics']
    )
    def get(self, request):
        data = AnalyticsQueries.get_product_performance()
        serializer = ProductPerformanceSerializer(data, many=True)
        return Response(serializer.data)


class CouponPerformanceView(APIView):
    """
    Get coupon usage and performance metrics.
    """
    permission_classes = [IsAuthenticated, IsAdminUser]

    @extend_schema(
        summary="Get Coupon Performance",
        description="Retrieve coupon usage statistics and discounts. Admin only.",
        responses={200: CouponPerformanceSerializer},
        tags=['Analytics']
    )
    def get(self, request):
        data = AnalyticsQueries.get_coupon_performance()
        serializer = CouponPerformanceSerializer(data)
        return Response(serializer.data)


class ReviewMetricsView(APIView):
    """
    Get review and rating metrics.
    """
    permission_classes = [IsAuthenticated, IsAdminUser]

    @extend_schema(
        summary="Get Review Metrics",
        description="Retrieve review statistics and rating distribution. Admin only.",
        responses={200: ReviewMetricsSerializer},
        tags=['Analytics']
    )
    def get(self, request):
        data = AnalyticsQueries.get_review_metrics()
        serializer = ReviewMetricsSerializer(data)
        return Response(serializer.data)


# ============================================================================
# AI Insights Views (Phase 2)
# ============================================================================

class WhatHappenedTodayView(APIView):
    """
    Get AI-generated summary of "What happened today?"

    Returns natural language explanation of today's performance.
    """
    permission_classes = [IsAuthenticated, IsAdminUser]

    @extend_schema(
        summary="What Happened Today?",
        description=(
            "Get AI-generated natural language summary of today's performance. "
            "Admin only."
        ),
        parameters=[
            OpenApiParameter(
                name='date',
                type=OpenApiTypes.DATE,
                location=OpenApiParameter.QUERY,
                description='Date to summarize (YYYY-MM-DD). Default: today',
                required=False
            )
        ],
        responses={200: DailySummarySerializer},
        tags=['AI Insights']
    )
    def get(self, request):
        date_param = request.query_params.get('date')

        # Parse date if provided
        if date_param:
            try:
                date = timezone.make_aware(
                    datetime.strptime(date_param, '%Y-%m-%d')
                )
            except ValueError:
                return Response(
                    {'error': 'Invalid date format. Use YYYY-MM-DD'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        else:
            date = timezone.now()

        data = AIInsightsService.generate_daily_summary(date)
        serializer = DailySummarySerializer(data)
        return Response(serializer.data)


class ExplainMetricView(APIView):
    """
    Get AI explanation for why a metric changed.

    Returns natural language explanation of metric changes.
    """
    permission_classes = [IsAuthenticated, IsAdminUser]

    @extend_schema(
        summary="Explain Metric Change",
        description=(
            "Get AI-generated explanation for why a metric changed. "
            "Provides natural language 'why' explanations. Admin only."
        ),
        parameters=[
            OpenApiParameter(
                name='metric',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Metric to explain (revenue, orders, users)',
                required=True
            ),
            OpenApiParameter(
                name='days',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description='Period to analyze (default: 30)',
                required=False
            )
        ],
        responses={200: MetricExplanationSerializer},
        tags=['AI Insights']
    )
    def get(self, request):
        metric_name = request.query_params.get('metric')
        days = int(request.query_params.get('days', 30))

        if not metric_name:
            return Response(
                {'error': 'Metric parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Validate metric name
        valid_metrics = ['revenue', 'orders', 'users']
        if metric_name not in valid_metrics:
            return Response(
                {
                    'error': f'Invalid metric. Must be one of: {", ".join(valid_metrics)}'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # Get current and previous period data
        end_date = timezone.now()
        start_date = end_date - timedelta(days=days)

        current_metrics = AnalyticsQueries.get_dashboard_kpis(days=days)

        # Extract the specific metric
        if metric_name == 'revenue':
            current_value = current_metrics['revenue']['current']
            previous_value = current_metrics['revenue']['previous']
        elif metric_name == 'orders':
            current_value = current_metrics['orders']['current']
            previous_value = current_metrics['orders']['previous']
        else:  # users
            current_value = current_metrics['active_users']
            previous_value = current_metrics['total_users'] * 0.7  # Estimate

        # Generate explanation
        data = AIInsightsService.explain_metric_change(
            metric_name, current_value, previous_value, days
        )
        serializer = MetricExplanationSerializer(data)
        return Response(serializer.data)


class BusinessInsightsView(APIView):
    """
    Get comprehensive AI business insights.

    Returns opportunities, warnings, and recommendations in natural language.
    """
    permission_classes = [IsAuthenticated, IsAdminUser]

    @extend_schema(
        summary="Get Business Insights",
        description=(
            "Get comprehensive AI-generated business insights including "
            "opportunities, warnings, and actionable recommendations. Admin only."
        ),
        parameters=[
            OpenApiParameter(
                name='days',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description='Period to analyze (default: 30)',
                required=False
            )
        ],
        responses={200: BusinessInsightsSerializer},
        tags=['AI Insights']
    )
    def get(self, request):
        days = int(request.query_params.get('days', 30))

        # Validate days parameter
        if days < 1 or days > 365:
            return Response(
                {'error': 'Days must be between 1 and 365'},
                status=status.HTTP_400_BAD_REQUEST
            )

        data = AIInsightsService.get_business_insights(days=days)
        serializer = BusinessInsightsSerializer(data)
        return Response(serializer.data)
