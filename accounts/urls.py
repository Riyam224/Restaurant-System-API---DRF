from django.urls import path
from .views import (
    RegisterAPIView,
    LoginAPIView,
    RefreshTokenAPIView,
    ProfileAPIView,
    ForgotPasswordAPIView,
    VerifyOTPAPIView,
    ResetPasswordAPIView,
)

app_name = "accounts"

urlpatterns = [
    # Authentication
    path("auth/register", RegisterAPIView.as_view(), name="register"),
    path("auth/login", LoginAPIView.as_view(), name="login"),
    path("auth/refresh", RefreshTokenAPIView.as_view(), name="refresh"),

    # User Profile
    path("profile", ProfileAPIView.as_view(), name="profile"),

    # Password Reset Flow (3 steps)
    path("auth/forgot-password", ForgotPasswordAPIView.as_view(), name="forgot-password"),
    path("auth/verify-otp", VerifyOTPAPIView.as_view(), name="verify-otp"),
    path("auth/reset-password", ResetPasswordAPIView.as_view(), name="reset-password"),
]
