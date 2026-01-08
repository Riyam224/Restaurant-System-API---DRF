from rest_framework import generics
from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiParameter,
    OpenApiResponse,
    extend_schema,
)

from .models import Category, Product
from .serializers import CategorySerializer, ProductSerializer
from core.permissions import ReadWithAPIKeyWriteWithJWT


# --------------------------------------------------
# CATEGORY LIST
# --------------------------------------------------
@extend_schema(
    tags=["Menu"],
    security=[{"ApiKeyAuth": []}, {"BearerAuth": []}],
    summary="List menu categories",
    description="Public endpoint. Returns all active menu categories.",
    responses={
        200: CategorySerializer(many=True),
        401: OpenApiResponse(description="Invalid or missing API key / token"),
    },
    examples=[
        OpenApiExample(
            "Categories Response",
            value=[
                {"id": 1, "name": "Burgers", "image": None, "is_active": True},
                {"id": 2, "name": "Drinks", "image": None, "is_active": True},
            ],
            response_only=True,
        )
    ],
)
class CategoryListAPIView(generics.ListAPIView):
    """
    Public API (API Key or JWT)

    Returns a list of active menu categories.
    """

    serializer_class = CategorySerializer
    permission_classes = [ReadWithAPIKeyWriteWithJWT]

    def get_queryset(self):
        return Category.objects.filter(is_active=True)


# --------------------------------------------------
# PRODUCT LIST
# --------------------------------------------------
@extend_schema(
    tags=["Menu"],
    security=[{"ApiKeyAuth": []}, {"BearerAuth": []}],
    summary="List available products",
    description=(
        "Public endpoint. Returns available products.\n\n"
        "Optional filter:\n"
        "- `category_id`: Filter products by category"
    ),
    parameters=[
        OpenApiParameter(
            name="category_id",
            required=False,
            type=int,
            location=OpenApiParameter.QUERY,
            description="Filter products by category id",
        )
    ],
    responses={
        200: ProductSerializer(many=True),
        401: OpenApiResponse(description="Invalid or missing API key / token"),
    },
    examples=[
        OpenApiExample(
            "Products Response",
            value=[
                {
                    "id": 10,
                    "category_id": 1,
                    "name": "Classic Burger",
                    "description": "Grilled beef patty, cheddar, and lettuce.",
                    "price": "12.50",
                    "image": "https://cdn.example.com/burger.jpg",
                    "is_available": True,
                }
            ],
            response_only=True,
        )
    ],
)
class ProductListAPIView(generics.ListAPIView):
    """
    Public API (API Key or JWT)

    Returns a list of available products.
    """

    serializer_class = ProductSerializer
    permission_classes = [ReadWithAPIKeyWriteWithJWT]

    def get_queryset(self):
        queryset = Product.objects.filter(is_available=True)

        category_id = self.request.query_params.get("category_id")
        if category_id:
            queryset = queryset.filter(category__id=category_id)

        return queryset.order_by("created_at")


# --------------------------------------------------
# PRODUCT DETAIL
# --------------------------------------------------
@extend_schema(
    tags=["Menu"],
    security=[{"ApiKeyAuth": []}, {"BearerAuth": []}],
    summary="Retrieve product details",
    description="Public endpoint. Returns details for a single available product.",
    responses={
        200: ProductSerializer,
        401: OpenApiResponse(description="Invalid or missing API key / token"),
        404: OpenApiResponse(description="Product not found"),
    },
    examples=[
        OpenApiExample(
            "Product Detail Response",
            value={
                "id": 10,
                "category_id": 1,
                "name": "Classic Burger",
                "description": "Grilled beef patty, cheddar, and lettuce.",
                "price": "12.50",
                "image": "https://cdn.example.com/burger.jpg",
                "is_available": True,
            },
            response_only=True,
        )
    ],
)
class ProductDetailAPIView(generics.RetrieveAPIView):
    """
    Public API (API Key or JWT)

    Returns single product details.
    """

    queryset = Product.objects.filter(is_available=True)
    serializer_class = ProductSerializer
    permission_classes = [ReadWithAPIKeyWriteWithJWT]
    lookup_field = "id"
