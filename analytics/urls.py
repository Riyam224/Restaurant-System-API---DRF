"""
Analytics URL configuration.
All endpoints are admin-only and read-only.
"""
from django.urls import path
from .views import (
    DashboardKPIsView,
    RevenueMetricsView,
    DailyRevenueView,
    OrderStatusView,
    UserMetricsView,
    ProductPerformanceView,
    CouponPerformanceView,
    ReviewMetricsView,
)

app_name = 'analytics'

urlpatterns = [
    # Dashboard KPIs - main endpoint for overview
    path('dashboard/', DashboardKPIsView.as_view(), name='dashboard-kpis'),

    # Revenue endpoints
    path('revenue/metrics/', RevenueMetricsView.as_view(), name='revenue-metrics'),
    path('revenue/daily/', DailyRevenueView.as_view(), name='daily-revenue'),

    # Order analytics
    path('orders/status/', OrderStatusView.as_view(), name='order-status'),

    # User analytics
    path('users/metrics/', UserMetricsView.as_view(), name='user-metrics'),

    # Product analytics
    path('products/performance/', ProductPerformanceView.as_view(), name='product-performance'),

    # Coupon analytics
    path('coupons/performance/', CouponPerformanceView.as_view(), name='coupon-performance'),

    # Review analytics
    path('reviews/metrics/', ReviewMetricsView.as_view(), name='review-metrics'),
]
