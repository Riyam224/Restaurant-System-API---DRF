from rest_framework import generics
from django.db.models import Q, Avg
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
    summary="List available products",
    description=(
        "Public endpoint. Returns available products with search and filtering.\n\n"
        "**Search & Filters:**\n"
        "- `search`: Search by product name or description\n"
        "- `category_id`: Filter by category\n"
        "- `min_price`: Minimum price filter\n"
        "- `max_price`: Maximum price filter\n"
        "- `sort_by`: Sort results (price_asc, price_desc, name, newest)\n"
    ),
    parameters=[
        OpenApiParameter(
            name="search",
            required=False,
            type=str,
            location=OpenApiParameter.QUERY,
            description="Search products by name or description",
        ),
        OpenApiParameter(
            name="category_id",
            required=False,
            type=int,
            location=OpenApiParameter.QUERY,
            description="Filter products by category id",
        ),
        OpenApiParameter(
            name="min_price",
            required=False,
            type=float,
            location=OpenApiParameter.QUERY,
            description="Minimum price filter",
        ),
        OpenApiParameter(
            name="max_price",
            required=False,
            type=float,
            location=OpenApiParameter.QUERY,
            description="Maximum price filter",
        ),
        OpenApiParameter(
            name="sort_by",
            required=False,
            type=str,
            location=OpenApiParameter.QUERY,
            description="Sort by: price_asc, price_desc, name, newest (default)",
        ),
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

    Returns a list of available products with search and advanced filtering.
    """

    serializer_class = ProductSerializer
    permission_classes = [ReadWithAPIKeyWriteWithJWT]

    def get_queryset(self):
        queryset = Product.objects.filter(is_available=True).select_related("category")

        # Search by name or description
        search = self.request.query_params.get("search")
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) | Q(description__icontains=search)
            )

        # Filter by category
        category_id = self.request.query_params.get("category_id")
        if category_id:
            queryset = queryset.filter(category__id=category_id)

        # Filter by price range
        min_price = self.request.query_params.get("min_price")
        if min_price:
            try:
                queryset = queryset.filter(price__gte=float(min_price))
            except ValueError:
                pass

        max_price = self.request.query_params.get("max_price")
        if max_price:
            try:
                queryset = queryset.filter(price__lte=float(max_price))
            except ValueError:
                pass

        # Sorting
        sort_by = self.request.query_params.get("sort_by", "newest")
        if sort_by == "price_asc":
            queryset = queryset.order_by("price")
        elif sort_by == "price_desc":
            queryset = queryset.order_by("-price")
        elif sort_by == "name":
            queryset = queryset.order_by("name")
        else:  # newest (default)
            queryset = queryset.order_by("-created_at")

        return queryset


# --------------------------------------------------
# PRODUCT DETAIL
# --------------------------------------------------
@extend_schema(
    tags=["Menu"],
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
