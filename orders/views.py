from django.db import transaction
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
from addresses.models import Address
from coupons.models import Coupon, CouponUsage
from .models import Order, OrderItem
from .serializers import OrderSerializer


@extend_schema(
    tags=["Orders"],
    summary="Create order from cart",
    description="Creates an order using the current user's cart items.",
    request=inline_serializer(
        name="CreateOrderRequest",
        fields={
            "address_id": serializers.IntegerField(),
            "coupon_code": serializers.CharField(required=False, allow_blank=True),
        },
    ),
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
                        "subtotal": "50.00",
                        "discount_amount": "5.00",
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
        401: OpenApiResponse(
            description="Authentication credentials were not provided."
        ),
    },
)
class CreateOrderAPIView(APIView):
    permission_classes = [IsAuthenticatedJWT]

    def post(self, request):
        user = request.user
        address_id = request.data.get("address_id")
        coupon_code = request.data.get("coupon_code", "").upper().strip()

        if not address_id:
            return Response(
                {"detail": "address_id is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        address = get_object_or_404(Address, id=address_id, user=user)
        cart_items = CartItem.objects.filter(cart__user=user).select_related("product")

        if not cart_items.exists():
            return Response(
                {"detail": "Cart is empty"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Validate all products are available
        unavailable_products = [
            item.product.name
            for item in cart_items
            if not item.product.is_available
        ]
        if unavailable_products:
            return Response(
                {
                    "detail": f"The following products are no longer available: {', '.join(unavailable_products)}"
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Calculate order subtotal using snapshot prices from cart
        subtotal = sum(item.price * item.quantity for item in cart_items)

        # Handle coupon if provided
        coupon = None
        discount_amount = 0
        if coupon_code:
            try:
                coupon = Coupon.objects.get(code=coupon_code)
                can_use, message = coupon.can_user_use(user)

                if not can_use:
                    return Response(
                        {"detail": message},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                if subtotal < coupon.minimum_order_amount:
                    return Response(
                        {
                            "detail": f"Minimum order amount of ${coupon.minimum_order_amount} required for this coupon"
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                discount_amount, final_amount = coupon.calculate_discount(subtotal)
            except Coupon.DoesNotExist:
                return Response(
                    {"detail": "Invalid coupon code"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        else:
            final_amount = subtotal

        with transaction.atomic():
            # Create order with pricing details
            order = Order.objects.create(
                user=user,
                address=address,
                subtotal=subtotal,
                discount_amount=discount_amount,
                total_price=final_amount,
                coupon_code=coupon_code if coupon else "",
            )

            # Create order items
            for item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product_id=item.product.id,
                    product_name=item.product.name,
                    price=item.product.price,
                    quantity=item.quantity,
                )

            # Record coupon usage
            if coupon:
                CouponUsage.objects.create(
                    coupon=coupon,
                    user=user,
                    order_id=order.id,
                    order_amount=subtotal,
                    discount_amount=discount_amount,
                    final_amount=final_amount,
                )
                coupon.increment_usage()

            # Clear cart
            cart_items.delete()

        return Response(
            {
                "message": "Order created successfully",
                "order_id": order.id,
                "status": order.status,
                "subtotal": str(order.subtotal),
                "discount_amount": str(order.discount_amount),
                "coupon_code": order.coupon_code,
                "total_price": str(order.total_price),
            },
            status=status.HTTP_201_CREATED,
        )


@extend_schema(
    tags=["Orders"],
    summary="List my orders",
    responses={
        200: OrderSerializer(many=True),
        401: OpenApiResponse(
            description="Authentication credentials were not provided."
        ),
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
        401: OpenApiResponse(
            description="Authentication credentials were not provided."
        ),
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
        401: OpenApiResponse(
            description="Authentication credentials were not provided."
        ),
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


class UpdateOrderStatusAPIView(APIView):
    """
    Order status endpoint:
    - GET: authenticated user (or admin) reads status
    - PATCH: admin updates status
    """

    def get_permissions(self):
        if self.request.method == "PATCH":
            return [IsAdminUserJWT()]
        return [IsAuthenticatedJWT()]

    @extend_schema(
        tags=["Orders"],
        summary="Get order status",
        description="Returns the current status and updated_at for an order.",
        parameters=[
            OpenApiParameter(
                name="pk",
                type=int,
                location=OpenApiParameter.PATH,
                description="Order ID",
            )
        ],
        responses={
            200: OpenApiResponse(
                response=inline_serializer(
                    name="OrderStatusResponse",
                    fields={
                        "order_id": serializers.IntegerField(),
                        "status": serializers.ChoiceField(
                            choices=[choice[0] for choice in Order.STATUS_CHOICES]
                        ),
                        "updated_at": serializers.DateTimeField(),
                    },
                ),
                description="Order status",
                examples=[
                    OpenApiExample(
                        "Order Status",
                        value={
                            "order_id": 12,
                            "status": "on_the_way",
                            "updated_at": "2026-01-14T12:30:00Z",
                        },
                        response_only=True,
                    )
                ],
            ),
            401: OpenApiResponse(
                description="Authentication credentials were not provided."
            ),
            404: OpenApiResponse(description="Order not found"),
        },
    )
    def get(self, request, pk):
        if request.user.is_staff:
            order = get_object_or_404(Order, pk=pk)
        else:
            order = get_object_or_404(Order, pk=pk, user=request.user)

        return Response(
            {
                "order_id": order.id,
                "status": order.status,
                "updated_at": order.updated_at,
            },
            status=status.HTTP_200_OK,
        )

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
                        value={
                            "message": "Order status updated",
                            "status": "preparing",
                        },
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
