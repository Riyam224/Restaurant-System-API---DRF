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
    # AI Insights views
    WhatHappenedTodayView,
    ExplainMetricView,
    BusinessInsightsView,
    # Anomaly Detection views (Phase 3)
    AnomalyDetectionView,
    AnomalySummaryView,
    DailyDigestView,
    # Prediction views (Phase 4)
    PredictTomorrowView,
    PredictPromoTimesView,
    PredictInventoryRisksView,
    PredictionSummaryView,
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

    # AI Insights endpoints (Phase 2)
    path('insights/today/', WhatHappenedTodayView.as_view(), name='what-happened-today'),
    path('insights/explain/', ExplainMetricView.as_view(), name='explain-metric'),
    path('insights/business/', BusinessInsightsView.as_view(), name='business-insights'),

    # Anomaly Detection endpoints (Phase 3)
    path('anomalies/detect/', AnomalyDetectionView.as_view(), name='detect-anomalies'),
    path('anomalies/summary/', AnomalySummaryView.as_view(), name='anomaly-summary'),
    path('anomalies/digest/', DailyDigestView.as_view(), name='daily-digest'),

    # Prediction endpoints (Phase 4)
    path('predictions/tomorrow/', PredictTomorrowView.as_view(), name='predict-tomorrow'),
    path('predictions/promo-times/', PredictPromoTimesView.as_view(), name='predict-promo-times'),
    path('predictions/inventory-risks/', PredictInventoryRisksView.as_view(), name='predict-inventory-risks'),
    path('predictions/summary/', PredictionSummaryView.as_view(), name='prediction-summary'),
]
