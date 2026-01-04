from cart.serialziers import CartSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Cart, CartItem
from menu.models import Product
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework import serializers
from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiParameter,
    OpenApiResponse,
    extend_schema,
    inline_serializer,
)


# Create your views here.
@extend_schema(
    tags=["Cart"],
    responses={
        200: CartSerializer,
        401: OpenApiResponse(description="Authentication credentials were not provided."),
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
    permission_classes = [IsAuthenticated]

    def get(self, request):
        cart, _ = Cart.objects.get_or_create(user=request.user)
        serializer = CartSerializer(cart)
        return Response(serializer.data)


@extend_schema(
    tags=["Cart"],
    request=inline_serializer(
        name="AddToCartRequest",
        fields={
            "product_id": serializers.IntegerField(),
            "quantity": serializers.IntegerField(required=False, default=1, min_value=1),
        },
    ),
    responses={
        200: OpenApiResponse(
            response=CartSerializer,
            description="Item added to cart",
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
        ),
        401: OpenApiResponse(description="Authentication credentials were not provided."),
        404: OpenApiResponse(
            description="Product not found",
            examples=[
                OpenApiExample(
                    "Product Missing",
                    value={"detail": "Not found."},
                    response_only=True,
                )
            ],
        ),
    },
)
class AddToCartAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        product_id = request.data.get("product_id")
        quantity = int(request.data.get("quantity", 1))

        product = get_object_or_404(Product, id=product_id)
        cart, _ = Cart.objects.get_or_create(user=request.user)

        item, created = CartItem.objects.get_or_create(
            cart=cart, product=product, defaults={"price": product.price}
        )

        if not created:
            item.quantity += quantity
        item.save()

        return Response(
            {
                "message": "Item added to cart",
                "cart": CartSerializer(cart).data,
            },
            status=200,
        )


@extend_schema(
    tags=["Cart"],
    parameters=[
        OpenApiParameter(
            name="item_id",
            type=int,
            location=OpenApiParameter.PATH,
            description="Cart item id to remove",
        )
    ],
    responses={
        200: OpenApiResponse(
            response=CartSerializer,
            description="Item removed",
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
        ),
        401: OpenApiResponse(description="Authentication credentials were not provided."),
        404: OpenApiResponse(
            description="Item not found",
            examples=[
                OpenApiExample(
                    "Missing Item",
                    value={"detail": "Not found."},
                    response_only=True,
                )
            ],
        ),
    },
)
class RemoveCartItemAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, item_id):
        item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
        item.delete()
        cart, _ = Cart.objects.get_or_create(user=request.user)
        return Response(
            {
                "message": "Item removed from cart",
                "cart": CartSerializer(cart).data,
            },
            status=status.HTTP_200_OK,
        )
