from django.urls import path
from .views import CartAPIView, AddToCartAPIView, RemoveCartItemAPIView


urlpatterns = [
    path("cart/", CartAPIView.as_view()),
    path("cart/add/", AddToCartAPIView.as_view()),
    path("cart/item/<int:item_id>/", RemoveCartItemAPIView.as_view()),
]
