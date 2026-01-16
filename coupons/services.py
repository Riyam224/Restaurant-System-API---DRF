"""
Coupon Service Layer
Handles all coupon-related business logic
"""
from decimal import Decimal
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import ValidationError

from .models import Coupon, CouponUsage


class CouponService:
    """Service class for coupon operations"""

    @staticmethod
    def validate_coupon(code: str, user, order_amount: Decimal):
        """
        Validate coupon for a given user and order amount

        Args:
            code: Coupon code
            user: User attempting to use the coupon
            order_amount: Order subtotal amount

        Returns:
            dict with validation result and discount preview

        Raises:
            ValidationError: If coupon is invalid
        """
        code = code.upper().strip()

        try:
            coupon = Coupon.objects.get(code=code)
        except Coupon.DoesNotExist:
            raise ValidationError("Invalid coupon code")

        # Check if user can use coupon
        can_use, message = coupon.can_user_use(user)
        if not can_use:
            raise ValidationError(message)

        # Check minimum order amount
        if order_amount < coupon.minimum_order_amount:
            raise ValidationError(
                f"Minimum order amount of ${coupon.minimum_order_amount} required"
            )

        # Calculate discount
        discount_amount, final_amount = coupon.calculate_discount(order_amount)

        return {
            "valid": True,
            "coupon_code": coupon.code,
            "discount_type": coupon.discount_type,
            "discount_value": str(coupon.discount_value),
            "order_amount": str(order_amount),
            "discount_amount": str(discount_amount),
            "final_amount": str(final_amount),
            "savings": str(discount_amount),
        }

    @staticmethod
    def get_user_available_coupons(user):
        """
        Get all coupons available for a specific user

        Args:
            user: User to get coupons for

        Returns:
            QuerySet of available coupons
        """
        from django.utils import timezone
        from django.db.models import Q, Count

        now = timezone.now()

        # Get coupons that are:
        # 1. Active
        # 2. Within valid date range
        # 3. Either public OR user-specific for this user
        # 4. Under total usage limit (if set)

        coupons = Coupon.objects.filter(
            is_active=True,
            valid_from__lte=now,
            valid_until__gte=now,
        ).filter(
            Q(is_user_specific=False) |
            Q(is_user_specific=True, allowed_users=user)
        ).annotate(
            user_usage_count=Count(
                'usages',
                filter=Q(usages__user=user)
            )
        )

        # Filter by usage limits
        available_coupons = []
        for coupon in coupons:
            # Check total usage limit
            if coupon.max_usage_total is not None and coupon.current_usage_count >= coupon.max_usage_total:
                continue

            # Check per-user usage limit
            if coupon.user_usage_count >= coupon.max_usage_per_user:
                continue

            available_coupons.append(coupon)

        return available_coupons

    @staticmethod
    def get_coupon_usage_stats(coupon_id: int):
        """
        Get usage statistics for a coupon

        Args:
            coupon_id: Coupon ID

        Returns:
            dict with usage statistics
        """
        coupon = get_object_or_404(Coupon, id=coupon_id)

        usages = CouponUsage.objects.filter(coupon=coupon)

        total_discount_given = sum(
            usage.discount_amount for usage in usages
        )

        return {
            "coupon_code": coupon.code,
            "total_uses": coupon.current_usage_count,
            "max_usage_total": coupon.max_usage_total,
            "usage_remaining": (
                coupon.max_usage_total - coupon.current_usage_count
                if coupon.max_usage_total
                else "unlimited"
            ),
            "total_discount_given": str(total_discount_given),
            "is_active": coupon.is_active,
        }
