from rest_framework import generics
from .models import Category, Product
from .serializers import CategorySerializer, ProductSerializer
from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiParameter,
    OpenApiResponse,
    extend_schema,
)


@extend_schema(
    tags=["Menu"],
    responses={
        200: CategorySerializer(many=True),
        401: OpenApiResponse(description="Authentication credentials were not provided."),
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
    Returns a list of active menu categories.
    """

    serializer_class = CategorySerializer

    def get_queryset(self):
        return Category.objects.filter(is_active=True)


@extend_schema(
    tags=["Menu"],
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
        401: OpenApiResponse(description="Authentication credentials were not provided."),
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
    Returns a list of available products.

    Optional query parameters:
    - category_id (int): Filter products by category
    """

    serializer_class = ProductSerializer

    def get_queryset(self):
        queryset = Product.objects.filter(is_available=True)

        category_id = self.request.query_params.get("category_id")
        if category_id is not None:
            queryset = queryset.filter(category__id=category_id)

        return queryset.order_by("created_at")


@extend_schema(
    tags=["Menu"],
    responses={
        200: ProductSerializer,
        401: OpenApiResponse(description="Authentication credentials were not provided."),
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
    Public API
    Returns single product details
    """

    queryset = Product.objects.filter(is_available=True)
    serializer_class = ProductSerializer
    lookup_field = "id"
