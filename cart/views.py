from django.shortcuts import get_object_or_404

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, serializers

from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiParameter,
    OpenApiResponse,
    extend_schema,
    inline_serializer,
)

from cart.serialziers import CartSerializer
from .models import Cart, CartItem
from menu.models import Product
from core.permissions import IsAuthenticatedJWT


# --------------------------------------------------
# GET CART
# --------------------------------------------------
@extend_schema(
    tags=["Cart"],
    security=[{"BearerAuth": []}],
    summary="Get user cart",
    description="Authenticated endpoint. Returns the current user's cart.",
    responses={
        200: CartSerializer,
        401: OpenApiResponse(
            description="Authentication credentials were not provided."
        ),
    },
    examples=[
        OpenApiExample(
            "Cart Response",
            value={
                "id": 1,
                "items": [
                    {
                        "id": 5,
                        "product_id": 10,
                        "name": "Classic Burger",
                        "price": "12.50",
                        "quantity": 2,
                        "subtotal": "25.00",
                    }
                ],
                "total_items": 2,
                "total_price": "25.00",
            },
            response_only=True,
        )
    ],
)
class CartAPIView(APIView):
    """
    Private API (JWT)
    Returns the authenticated user's cart.
    """

    permission_classes = [IsAuthenticatedJWT]

    def get(self, request):
        cart, _ = Cart.objects.get_or_create(user=request.user)
        serializer = CartSerializer(cart)
        return Response(serializer.data, status=status.HTTP_200_OK)


# --------------------------------------------------
# ADD TO CART
# --------------------------------------------------
@extend_schema(
    tags=["Cart"],
    security=[{"BearerAuth": []}],
    summary="Add product to cart",
    description="Authenticated endpoint. Adds a product to the user's cart.",
    request=inline_serializer(
        name="AddToCartRequest",
        fields={
            "product_id": serializers.IntegerField(),
            "quantity": serializers.IntegerField(
                required=False,
                default=1,
                min_value=1,
            ),
        },
    ),
    responses={
        200: OpenApiResponse(
            response=CartSerializer,
            description="Item added to cart",
        ),
        401: OpenApiResponse(
            description="Authentication credentials were not provided."
        ),
        404: OpenApiResponse(description="Product not found"),
    },
    examples=[
        OpenApiExample(
            "Add Item Response",
            value={
                "message": "Item added to cart",
                "cart": {
                    "id": 1,
                    "items": [
                        {
                            "id": 5,
                            "product_id": 10,
                            "name": "Classic Burger",
                            "price": "12.50",
                            "quantity": 2,
                            "subtotal": "25.00",
                        }
                    ],
                    "total_items": 2,
                    "total_price": "25.00",
                },
            },
            response_only=True,
        )
    ],
)
class AddToCartAPIView(APIView):
    """
    Private API (JWT)
    Adds a product to the authenticated user's cart.
    """

    permission_classes = [IsAuthenticatedJWT]

    def post(self, request):
        # Validate input
        serializer = inline_serializer(
            fields={
                "product_id": serializers.IntegerField(),
                "quantity": serializers.IntegerField(
                    required=False,
                    default=1,
                    min_value=1,
                ),
            },
            data=request.data,
        )
        serializer.is_valid(raise_exception=True)

        product_id = serializer.validated_data["product_id"]
        quantity = serializer.validated_data["quantity"]

        product = get_object_or_404(Product, id=product_id)
        cart, _ = Cart.objects.get_or_create(user=request.user)

        item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={"price": product.price},
        )

        if created:
            item.quantity = quantity
        else:
            item.quantity += quantity

        item.save()

        return Response(
            {
                "message": "Item added to cart",
                "cart": CartSerializer(cart).data,
            },
            status=status.HTTP_200_OK,
        )


# --------------------------------------------------
# REMOVE CART ITEM
# --------------------------------------------------
@extend_schema(
    tags=["Cart"],
    security=[{"BearerAuth": []}],
    summary="Remove item from cart",
    description="Authenticated endpoint. Removes an item from the user's cart.",
    parameters=[
        OpenApiParameter(
            name="item_id",
            type=int,
            location=OpenApiParameter.PATH,
            description="Cart item ID",
        )
    ],
    responses={
        200: OpenApiResponse(
            response=CartSerializer,
            description="Item removed",
        ),
        401: OpenApiResponse(
            description="Authentication credentials were not provided."
        ),
        404: OpenApiResponse(description="Item not found"),
    },
    examples=[
        OpenApiExample(
            "Remove Item Response",
            value={
                "message": "Item removed from cart",
                "cart": {
                    "id": 1,
                    "items": [],
                    "total_items": 0,
                    "total_price": "0.00",
                },
            },
            response_only=True,
        )
    ],
)
class RemoveCartItemAPIView(APIView):
    """
    Private API (JWT)
    Removes an item from the authenticated user's cart.
    """

    permission_classes = [IsAuthenticatedJWT]

    def delete(self, request, item_id):
        item = get_object_or_404(
            CartItem,
            id=item_id,
            cart__user=request.user,
        )

        item.delete()

        cart, _ = Cart.objects.get_or_create(user=request.user)

        return Response(
            {
                "message": "Item removed from cart",
                "cart": CartSerializer(cart).data,
            },
            status=status.HTTP_200_OK,
        )
