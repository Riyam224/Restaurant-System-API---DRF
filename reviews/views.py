from rest_framework import status
from rest_framework.generics import (
    ListAPIView,
    CreateAPIView,
    RetrieveUpdateDestroyAPIView,
)
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiParameter,
    OpenApiResponse,
    extend_schema,
    inline_serializer,
)
from rest_framework import serializers as drf_serializers

from core.permissions import IsAuthenticatedJWT
from .models import Review, ReviewHelpfulness
from .serializers import (
    ReviewSerializer,
    ReviewCreateSerializer,
    ReviewUpdateSerializer,
    ReviewHelpfulnessSerializer,
    ProductRatingStatsSerializer,
)


@extend_schema(
    tags=["Reviews"],
    summary="List reviews for a product",
    description="Get all approved reviews for a specific product with pagination.",
    parameters=[
        OpenApiParameter(
            name="product_id",
            type=int,
            location=OpenApiParameter.QUERY,
            description="Product ID to filter reviews",
            required=True,
        ),
        OpenApiParameter(
            name="rating",
            type=int,
            location=OpenApiParameter.QUERY,
            description="Filter by rating (1-5)",
            required=False,
        ),
    ],
    responses={
        200: ReviewSerializer(many=True),
        400: OpenApiResponse(description="Product ID is required"),
    },
)
class ReviewListAPIView(ListAPIView):
    """List all approved reviews for a product."""

    serializer_class = ReviewSerializer
    permission_classes = []  # Public endpoint

    def get_queryset(self):
        product_id = self.request.query_params.get("product_id")
        if not product_id:
            return Review.objects.none()

        queryset = Review.objects.filter(
            product_id=product_id,
            is_approved=True
        ).select_related("user").prefetch_related("helpfulness_votes")

        # Filter by rating if provided
        rating = self.request.query_params.get("rating")
        if rating and rating.isdigit():
            queryset = queryset.filter(rating=int(rating))

        return queryset


@extend_schema(
    tags=["Reviews"],
    summary="Create a review",
    description="Create a new review for a product. Users can only review each product once.",
    request=ReviewCreateSerializer,
    responses={
        201: ReviewSerializer,
        400: OpenApiResponse(
            description="Validation error or already reviewed",
            examples=[
                OpenApiExample(
                    "Already Reviewed",
                    value={"detail": "You have already reviewed this product."},
                )
            ],
        ),
        401: OpenApiResponse(
            description="Authentication credentials were not provided."
        ),
    },
)
class ReviewCreateAPIView(CreateAPIView):
    """Create a new review."""

    serializer_class = ReviewCreateSerializer
    permission_classes = [IsAuthenticatedJWT]

    def perform_create(self, serializer):
        serializer.save()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        # Return full review details
        review = serializer.instance
        output_serializer = ReviewSerializer(review, context={"request": request})
        return Response(
            output_serializer.data,
            status=status.HTTP_201_CREATED
        )


@extend_schema(
    tags=["Reviews"],
    summary="Get, update, or delete a review",
    description="Manage a specific review. Only the review owner can update/delete within 7 days.",
    responses={
        200: ReviewSerializer,
        204: OpenApiResponse(description="Review deleted"),
        400: OpenApiResponse(description="Cannot edit after 7 days"),
        401: OpenApiResponse(
            description="Authentication credentials were not provided."
        ),
        403: OpenApiResponse(description="Not the review owner"),
        404: OpenApiResponse(description="Review not found"),
    },
)
class ReviewDetailAPIView(RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete a review."""

    permission_classes = [IsAuthenticatedJWT]

    def get_serializer_class(self):
        if self.request.method in ["PUT", "PATCH"]:
            return ReviewUpdateSerializer
        return ReviewSerializer

    def get_queryset(self):
        # Users can only manage their own reviews
        return Review.objects.filter(user=self.request.user)


@extend_schema(
    tags=["Reviews"],
    summary="List my reviews",
    description="Get all reviews created by the authenticated user.",
    responses={
        200: ReviewSerializer(many=True),
        401: OpenApiResponse(
            description="Authentication credentials were not provided."
        ),
    },
)
class MyReviewsAPIView(ListAPIView):
    """List all reviews by the authenticated user."""

    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticatedJWT]

    def get_queryset(self):
        return Review.objects.filter(user=self.request.user).order_by("-created_at")


@extend_schema(
    tags=["Reviews"],
    summary="Get product rating statistics",
    description="Get average rating and rating distribution for a product.",
    parameters=[
        OpenApiParameter(
            name="product_id",
            type=int,
            location=OpenApiParameter.PATH,
            description="Product ID",
            required=True,
        ),
    ],
    responses={
        200: OpenApiResponse(
            response=ProductRatingStatsSerializer,
            description="Product rating statistics",
            examples=[
                OpenApiExample(
                    "Rating Stats",
                    value={
                        "average_rating": 4.25,
                        "total_reviews": 120,
                        "rating_distribution": {
                            "5": 60,
                            "4": 40,
                            "3": 15,
                            "2": 3,
                            "1": 2,
                            "total": 120,
                        },
                    },
                )
            ],
        ),
    },
)
class ProductRatingStatsAPIView(APIView):
    """Get rating statistics for a product."""

    permission_classes = []  # Public endpoint

    def get(self, request, product_id):
        average_rating = Review.get_product_average_rating(product_id)
        rating_distribution = Review.get_product_rating_distribution(product_id)

        data = {
            "average_rating": average_rating,
            "total_reviews": rating_distribution["total"],
            "rating_distribution": rating_distribution,
        }

        serializer = ProductRatingStatsSerializer(data)
        return Response(serializer.data, status=status.HTTP_200_OK)


@extend_schema(
    tags=["Reviews"],
    summary="Mark review as helpful/not helpful",
    description="Vote on whether a review was helpful. Users cannot vote on their own reviews.",
    request=inline_serializer(
        name="ReviewHelpfulnessRequest",
        fields={
            "review_id": drf_serializers.IntegerField(),
            "is_helpful": drf_serializers.BooleanField(),
        },
    ),
    responses={
        201: OpenApiResponse(
            description="Vote recorded",
            examples=[
                OpenApiExample(
                    "Vote Recorded",
                    value={"message": "Your vote has been recorded"},
                )
            ],
        ),
        400: OpenApiResponse(
            description="Already voted or voting on own review",
            examples=[
                OpenApiExample(
                    "Already Voted",
                    value={"detail": "You have already voted on this review."},
                )
            ],
        ),
        401: OpenApiResponse(
            description="Authentication credentials were not provided."
        ),
        404: OpenApiResponse(description="Review not found"),
    },
)
class ReviewHelpfulnessAPIView(APIView):
    """Mark a review as helpful or not helpful."""

    permission_classes = [IsAuthenticatedJWT]

    def post(self, request):
        review_id = request.data.get("review_id")
        is_helpful = request.data.get("is_helpful")

        if review_id is None or is_helpful is None:
            return Response(
                {"detail": "review_id and is_helpful are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        review = get_object_or_404(Review, id=review_id)

        serializer = ReviewHelpfulnessSerializer(
            data={"review": review.id, "is_helpful": is_helpful},
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {"message": "Your vote has been recorded"},
            status=status.HTTP_201_CREATED,
        )
