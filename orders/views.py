from django.shortcuts import get_object_or_404
from rest_framework import serializers, status
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiParameter,
    OpenApiResponse,
    extend_schema,
    inline_serializer,
)

from core.permissions import IsAdminUserJWT, IsAuthenticatedJWT
from cart.models import CartItem
from .models import Order, OrderItem
from .serializers import OrderSerializer


@extend_schema(
    tags=["Orders"],
    summary="Create order from cart",
    description="Creates an order using the current user's cart items.",
    request=None,
    responses={
        201: OpenApiResponse(
            description="Order created",
            examples=[
                OpenApiExample(
                    "Order Created",
                    value={
                        "message": "Order created successfully",
                        "order_id": 15,
                        "status": "pending",
                        "total_price": "45.00",
                    },
                    response_only=True,
                )
            ],
        ),
        400: OpenApiResponse(
            description="Cart is empty",
            examples=[OpenApiExample("Empty Cart", value={"detail": "Cart is empty"})],
        ),
        401: OpenApiResponse(description="Authentication credentials were not provided."),
    },
)
class CreateOrderAPIView(APIView):
    """
    User API (JWT)
    Creates an order using the authenticated user's cart items.
    """

    permission_classes = [IsAuthenticatedJWT]

    def post(self, request):
        user = request.user
        cart_items = CartItem.objects.filter(cart__user=user)

        if not cart_items.exists():
            return Response(
                {"detail": "Cart is empty"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        total_price = sum(item.subtotal() for item in cart_items)

        order = Order.objects.create(
            user=user,
            total_price=total_price,
        )

        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product_id=item.product.id,
                product_name=item.product.name,
                price=item.product.price,
                quantity=item.quantity,
            )

        cart_items.delete()

        return Response(
            {
                "message": "Order created successfully",
                "order_id": order.id,
                "status": order.status,
                "total_price": order.total_price,
            },
            status=status.HTTP_201_CREATED,
        )


@extend_schema(
    tags=["Orders"],
    summary="List my orders",
    responses={
        200: OrderSerializer(many=True),
        401: OpenApiResponse(description="Authentication credentials were not provided."),
    },
)
class UserOrdersAPIView(ListAPIView):
    """
    User API (JWT)
    Lists the authenticated user's orders.
    """

    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticatedJWT]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).order_by("-created_at")


@extend_schema(
    tags=["Orders"],
    summary="List my orders (alias)",
    responses={
        200: OrderSerializer(many=True),
        401: OpenApiResponse(description="Authentication credentials were not provided."),
    },
)
class OrderListAPIView(ListAPIView):
    """
    User API (JWT)
    Lists the authenticated user's orders (alias endpoint).
    """

    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticatedJWT]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)


@extend_schema(
    tags=["Orders"],
    summary="Get order details",
    responses={
        200: OrderSerializer,
        401: OpenApiResponse(description="Authentication credentials were not provided."),
        404: OpenApiResponse(description="Order not found"),
    },
)
class OrderDetailAPIView(RetrieveAPIView):
    """
    User API (JWT)
    Retrieves a single order for the authenticated user.
    """

    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticatedJWT]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)


@extend_schema(
    tags=["Orders"],
    summary="Update order status (admin)",
    description="Admin-only endpoint. Updates order status.",
    parameters=[
        OpenApiParameter(
            name="pk",
            type=int,
            location=OpenApiParameter.PATH,
            description="Order ID",
        )
    ],
    request=inline_serializer(
        name="OrderStatusUpdateRequest",
        fields={
            "status": serializers.ChoiceField(
                choices=[choice[0] for choice in Order.STATUS_CHOICES]
            )
        },
    ),
    responses={
        200: OpenApiResponse(
            description="Status updated",
            examples=[
                OpenApiExample(
                    "Status Updated",
                    value={"message": "Order status updated", "status": "preparing"},
                    response_only=True,
                )
            ],
        ),
        400: OpenApiResponse(description="Invalid status"),
        401: OpenApiResponse(
            description="Authentication credentials were not provided."
        ),
        404: OpenApiResponse(description="Order not found"),
    },
)
class UpdateOrderStatusAPIView(APIView):
    """
    Admin API (JWT)
    Updates order status.
    """

    permission_classes = [IsAdminUserJWT]

    def patch(self, request, pk):
        order = get_object_or_404(Order, pk=pk)

        serializer = inline_serializer(
            name="OrderStatusUpdateValidator",
            fields={
                "status": serializers.ChoiceField(
                    choices=[choice[0] for choice in Order.STATUS_CHOICES]
                )
            },
            data=request.data,
        )
        serializer.is_valid(raise_exception=True)

        order.status = serializer.validated_data["status"]
        order.save()

        return Response(
            {
                "message": "Order status updated",
                "status": order.status,
            },
            status=status.HTTP_200_OK,
        )
