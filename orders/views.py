from rest_framework import serializers
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiParameter,
    OpenApiResponse,
    extend_schema,
    inline_serializer,
)

from cart.models import CartItem
from .models import Order, OrderItem
from .serializers import OrderSerializer


@extend_schema(
    tags=["Orders"],
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
            examples=[
                OpenApiExample(
                    "Empty Cart",
                    value={"detail": "Cart is empty"},
                    response_only=True,
                )
            ],
        ),
        401: OpenApiResponse(description="Authentication credentials were not provided."),
    },
)
class CreateOrderAPIView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = OrderSerializer

    def post(self, request):
        user = request.user
        cart_items = CartItem.objects.filter(user=user)

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
    responses={
        200: OrderSerializer(many=True),
        401: OpenApiResponse(description="Authentication credentials were not provided."),
    },
)
class UserOrdersAPIView(ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).order_by("-created_at")


@extend_schema(
    tags=["Orders"],
    responses={
        200: OrderSerializer(many=True),
        401: OpenApiResponse(description="Authentication credentials were not provided."),
    },
)
class OrderListAPIView(ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)


@extend_schema(
    tags=["Orders"],
    responses={
        200: OrderSerializer,
        401: OpenApiResponse(description="Authentication credentials were not provided."),
        404: OpenApiResponse(description="Order not found"),
    },
)
class OrderDetailAPIView(RetrieveAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)


@extend_schema(
    tags=["Orders"],
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
        400: OpenApiResponse(
            description="Invalid status",
            examples=[
                OpenApiExample(
                    "Invalid Status",
                    value={"detail": "Invalid status"},
                    response_only=True,
                )
            ],
        ),
        401: OpenApiResponse(description="Authentication credentials were not provided."),
        404: OpenApiResponse(description="Order not found"),
    },
)
class UpdateOrderStatusAPIView(APIView):
    permission_classes = [IsAdminUser]

    def patch(self, request, pk):
        order = Order.objects.get(pk=pk)
        new_status = request.data.get("status")

        if new_status not in dict(Order.STATUS_CHOICES):
            return Response(
                {"detail": "Invalid status"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        order.status = new_status
        order.save()

        return Response(
            {
                "message": "Order status updated",
                "status": order.status,
            }
        )
