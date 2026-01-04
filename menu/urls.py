from django.urls import path
from .views import CategoryListAPIView, ProductDetailAPIView, ProductListAPIView


urlpatterns = [
    path("categories/", CategoryListAPIView.as_view(), name="category-list"),
    path("products/", ProductListAPIView.as_view(), name="product-list"),
    path("products/<int:id>/", ProductDetailAPIView.as_view()),
]
