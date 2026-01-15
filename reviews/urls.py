from django.urls import path
from . import views

urlpatterns = [
    # Review CRUD
    path("reviews/", views.ReviewListAPIView.as_view(), name="review-list"),
    path("reviews/create/", views.ReviewCreateAPIView.as_view(), name="review-create"),
    path("reviews/<int:pk>/", views.ReviewDetailAPIView.as_view(), name="review-detail"),
    path("reviews/my/", views.MyReviewsAPIView.as_view(), name="my-reviews"),

    # Product rating stats
    path(
        "products/<int:product_id>/ratings/",
        views.ProductRatingStatsAPIView.as_view(),
        name="product-ratings",
    ),

    # Review helpfulness
    path(
        "reviews/helpful/",
        views.ReviewHelpfulnessAPIView.as_view(),
        name="review-helpful",
    ),
]
