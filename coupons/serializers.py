from rest_framework import serializers
from django.utils import timezone
from decimal import Decimal
from drf_spectacular.utils import extend_schema_field
from .models import Coupon, CouponUsage


class CouponSerializer(serializers.ModelSerializer):
    """Serializer for listing and retrieving coupons."""

    discount_display = serializers.CharField(source="get_discount_display", read_only=True)
    is_valid = serializers.SerializerMethodField()
    usage_info = serializers.SerializerMethodField()

    class Meta:
        model = Coupon
        fields = [
            "id",
            "code",
            "description",
            "discount_type",
            "discount_value",
            "discount_display",
            "minimum_order_amount",
            "maximum_discount_amount",
            "max_usage_per_user",
            "valid_from",
            "valid_until",
            "is_active",
            "is_valid",
            "usage_info",
        ]
        read_only_fields = ["id"]

    @extend_schema_field(serializers.BooleanField)
    def get_is_valid(self, obj) -> bool:
        """Check if coupon is currently valid."""
        return obj.is_valid()

    @extend_schema_field(serializers.DictField)
    def get_usage_info(self, obj) -> dict:
        """Get usage statistics."""
        request = self.context.get("request")
        info = {
            "current_usage": obj.current_usage_count,
            "max_usage_total": obj.max_usage_total,
        }

        if request and request.user.is_authenticated:
            user_usage = CouponUsage.objects.filter(
                coupon=obj,
                user=request.user
            ).count()
            info["user_usage"] = user_usage
            info["user_can_use"] = user_usage < obj.max_usage_per_user

        return info


class CouponValidateSerializer(serializers.Serializer):
    """Serializer for validating coupon codes."""

    code = serializers.CharField(
        max_length=50,
        help_text="Coupon code to validate"
    )
    order_amount = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        min_value=Decimal("0.01"),
        help_text="Order amount before discount"
    )

    def validate_code(self, value):
        """Validate coupon code exists and is uppercase."""
        return value.upper().strip()


class CouponApplySerializer(serializers.Serializer):
    """Serializer for applying coupon to order."""

    coupon_code = serializers.CharField(
        max_length=50,
        required=False,
        allow_blank=True,
        help_text="Optional coupon code"
    )

    def validate_coupon_code(self, value):
        """Clean and validate coupon code."""
        if value:
            return value.upper().strip()
        return None


class CouponUsageSerializer(serializers.ModelSerializer):
    """Serializer for coupon usage history."""

    coupon_code = serializers.CharField(source="coupon.code", read_only=True)
    coupon_description = serializers.CharField(source="coupon.description", read_only=True)

    class Meta:
        model = CouponUsage
        fields = [
            "id",
            "coupon_code",
            "coupon_description",
            "order_id",
            "order_amount",
            "discount_amount",
            "final_amount",
            "used_at",
        ]
        read_only_fields = fields


class CouponAdminSerializer(serializers.ModelSerializer):
    """Admin serializer for creating/updating coupons."""

    class Meta:
        model = Coupon
        fields = [
            "id",
            "code",
            "description",
            "discount_type",
            "discount_value",
            "minimum_order_amount",
            "maximum_discount_amount",
            "max_usage_total",
            "max_usage_per_user",
            "current_usage_count",
            "is_user_specific",
            "valid_from",
            "valid_until",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "current_usage_count", "created_at", "updated_at"]

    def validate_code(self, value):
        """Ensure code is uppercase and unique."""
        value = value.upper().strip()
        if not value:
            raise serializers.ValidationError("Code cannot be empty.")
        return value

    def validate_discount_value(self, value):
        """Validate discount value based on type."""
        if value <= 0:
            raise serializers.ValidationError("Discount value must be greater than 0.")
        return value

    def validate(self, attrs):
        """Cross-field validation."""
        discount_type = attrs.get("discount_type", self.instance.discount_type if self.instance else None)
        discount_value = attrs.get("discount_value")

        # Validate percentage
        if discount_type == "percentage" and discount_value:
            if discount_value > 100:
                raise serializers.ValidationError({
                    "discount_value": "Percentage discount cannot exceed 100%."
                })

        # Validate dates
        valid_from = attrs.get("valid_from", self.instance.valid_from if self.instance else None)
        valid_until = attrs.get("valid_until", self.instance.valid_until if self.instance else None)

        if valid_from and valid_until and valid_from >= valid_until:
            raise serializers.ValidationError({
                "valid_until": "End date must be after start date."
            })

        return attrs
