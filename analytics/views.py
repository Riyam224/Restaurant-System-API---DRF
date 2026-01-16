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
from .serializers import (
    RevenueMetricsSerializer,
    DailyRevenueSerializer,
    OrderStatusBreakdownSerializer,
    UserMetricsSerializer,
    ProductPerformanceSerializer,
    CouponPerformanceSerializer,
    ReviewMetricsSerializer,
    DashboardKPIsSerializer,
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
