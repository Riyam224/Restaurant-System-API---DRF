from django.urls import path
from .views import CreateOrderAPIView, OrderDetailAPIView, OrderListAPIView, UpdateOrderStatusAPIView

urlpatterns = [
    path("orders/create/", CreateOrderAPIView.as_view(), name="create-order"),
    path("orders/", OrderListAPIView.as_view(), name="orders-list"),
    path("orders/<int:pk>/", OrderDetailAPIView.as_view(), name="order-detail"),
    path(
        "orders/<int:pk>/status/",
        UpdateOrderStatusAPIView.as_view(),
        name="order-status",
    ),
]
