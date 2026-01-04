from django.urls import path
from .views import RegisterAPIView, LoginAPIView, RefreshTokenAPIView, ProfileAPIView

urlpatterns = [
    path("auth/register", RegisterAPIView.as_view(), name="register"),
    path("auth/login", LoginAPIView.as_view(), name="login"),
    path("auth/refresh", RefreshTokenAPIView.as_view(), name="refresh"),
    path("profile", ProfileAPIView.as_view(), name="profile"),
]
