from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db import models
from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiParameter,
    OpenApiResponse,
    extend_schema,
)

from core.permissions import IsAuthenticatedJWT, IsAdminUserJWT
from .models import Coupon, CouponUsage
from .serializers import (
    CouponSerializer,
    CouponValidateSerializer,
    CouponUsageSerializer,
)


@extend_schema(
    tags=["Coupons"],
    summary="List available coupons",
    description="Get all active and valid coupons. Admins see all, users see public coupons.",
    responses={
        200: CouponSerializer(many=True),
        401: OpenApiResponse(
            description="Authentication credentials were not provided."
        ),
    },
)
class CouponListAPIView(ListAPIView):
    """List all available coupons."""

    serializer_class = CouponSerializer
    permission_classes = [IsAuthenticatedJWT]

    def get_queryset(self):
        user = self.request.user
        now = timezone.now()

        queryset = Coupon.objects.filter(
            is_active=True,
            valid_from__lte=now,
            valid_until__gte=now,
        )

        # Non-admin users only see non-user-specific or their exclusive coupons
        if not user.is_staff:
            queryset = queryset.filter(
                models.Q(is_user_specific=False) |
                models.Q(allowed_users=user)
            ).distinct()

        return queryset.order_by("-created_at")


@extend_schema(
    tags=["Coupons"],
    summary="Validate coupon code",
    description="Check if a coupon code is valid and calculate potential discount.",
    request=CouponValidateSerializer,
    responses={
        200: OpenApiResponse(
            description="Coupon validated successfully",
            examples=[
                OpenApiExample(
                    "Valid Coupon",
                    value={
                        "valid": True,
                        "message": "Coupon is valid",
                        "coupon": {
                            "code": "SUMMER20",
                            "discount_type": "percentage",
                            "discount_value": "20.00",
                            "discount_display": "20% off",
                        },
                        "discount_amount": "10.00",
                        "final_amount": "40.00",
                    },
                )
            ],
        ),
        400: OpenApiResponse(
            description="Invalid coupon",
            examples=[
                OpenApiExample(
                    "Invalid Coupon",
                    value={
                        "valid": False,
                        "message": "Coupon is not valid",
                    },
                ),
                OpenApiExample(
                    "Minimum Not Met",
                    value={
                        "valid": False,
                        "message": "Minimum order amount of $30.00 required",
                    },
                ),
            ],
        ),
        401: OpenApiResponse(
            description="Authentication credentials were not provided."
        ),
        404: OpenApiResponse(description="Coupon not found"),
    },
)
class CouponValidateAPIView(APIView):
    """Validate a coupon code and calculate discount."""

    permission_classes = [IsAuthenticatedJWT]

    def post(self, request):
        serializer = CouponValidateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        code = serializer.validated_data["code"]
        order_amount = serializer.validated_data["order_amount"]

        try:
            coupon = Coupon.objects.get(code=code)
        except Coupon.DoesNotExist:
            return Response(
                {
                    "valid": False,
                    "message": "Coupon code not found",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        # Check if user can use coupon
        can_use, message = coupon.can_user_use(request.user)

        if not can_use:
            return Response(
                {
                    "valid": False,
                    "message": message,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Check minimum order amount
        if order_amount < coupon.minimum_order_amount:
            return Response(
                {
                    "valid": False,
                    "message": f"Minimum order amount of ${coupon.minimum_order_amount} required",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Calculate discount
        discount_amount, final_amount = coupon.calculate_discount(order_amount)

        return Response(
            {
                "valid": True,
                "message": "Coupon is valid",
                "coupon": {
                    "code": coupon.code,
                    "discount_type": coupon.discount_type,
                    "discount_value": str(coupon.discount_value),
                    "discount_display": coupon.get_discount_display(),
                },
                "discount_amount": str(discount_amount),
                "final_amount": str(final_amount),
            },
            status=status.HTTP_200_OK,
        )


@extend_schema(
    tags=["Coupons"],
    summary="Get my coupon usage history",
    description="List all coupons used by the authenticated user.",
    responses={
        200: CouponUsageSerializer(many=True),
        401: OpenApiResponse(
            description="Authentication credentials were not provided."
        ),
    },
)
class MyCouponUsageAPIView(ListAPIView):
    """List user's coupon usage history."""

    serializer_class = CouponUsageSerializer
    permission_classes = [IsAuthenticatedJWT]

    def get_queryset(self):
        return CouponUsage.objects.filter(
            user=self.request.user
        ).select_related("coupon").order_by("-used_at")


@extend_schema(
    tags=["Coupons"],
    summary="Get coupon by code",
    description="Get details of a specific coupon by its code.",
    parameters=[
        OpenApiParameter(
            name="code",
            type=str,
            location=OpenApiParameter.PATH,
            description="Coupon code",
            required=True,
        ),
    ],
    responses={
        200: CouponSerializer,
        401: OpenApiResponse(
            description="Authentication credentials were not provided."
        ),
        404: OpenApiResponse(description="Coupon not found"),
    },
)
class CouponDetailAPIView(APIView):
    """Get coupon details by code."""

    permission_classes = [IsAuthenticatedJWT]

    def get(self, request, code):
        code = code.upper().strip()
        coupon = get_object_or_404(
            Coupon,
            code=code,
            is_active=True
        )

        # Check if user can see this coupon
        user = request.user
        if not user.is_staff:
            if coupon.is_user_specific and not coupon.allowed_users.filter(id=user.id).exists():
                return Response(
                    {"detail": "Coupon not found"},
                    status=status.HTTP_404_NOT_FOUND,
                )

        serializer = CouponSerializer(coupon, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)
