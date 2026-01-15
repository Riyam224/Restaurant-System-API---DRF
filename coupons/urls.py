from django.urls import path
from . import views

urlpatterns = [
    path("coupons/", views.CouponListAPIView.as_view(), name="coupon-list"),
    path("coupons/validate/", views.CouponValidateAPIView.as_view(), name="coupon-validate"),
    path("coupons/my-usage/", views.MyCouponUsageAPIView.as_view(), name="my-coupon-usage"),
    path("coupons/<str:code>/", views.CouponDetailAPIView.as_view(), name="coupon-detail"),
]
