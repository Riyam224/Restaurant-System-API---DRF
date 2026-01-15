from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from decimal import Decimal

User = get_user_model()


class Coupon(models.Model):
    """
    Discount coupon for orders.

    Business Rules:
    - Can be percentage or fixed amount discount
    - Can have minimum order requirement
    - Can limit total usage and per-user usage
    - Can be restricted to specific users
    - Must be active and within valid date range
    - Auto-deactivated when usage limit reached
    """

    DISCOUNT_TYPE_CHOICES = (
        ("percentage", "Percentage"),
        ("fixed", "Fixed Amount"),
    )

    # Basic Information
    code = models.CharField(
        max_length=50,
        unique=True,
        db_index=True,
        help_text="Coupon code (e.g., SUMMER20, FIRST10)"
    )
    description = models.TextField(
        help_text="Internal description of the coupon"
    )

    # Discount Configuration
    discount_type = models.CharField(
        max_length=20,
        choices=DISCOUNT_TYPE_CHOICES,
        default="percentage"
    )
    discount_value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
        help_text="Percentage (1-100) or fixed amount"
    )

    # Restrictions
    minimum_order_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Minimum order amount to apply coupon"
    )
    maximum_discount_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
        help_text="Maximum discount amount (for percentage coupons)"
    )

    # Usage Limits
    max_usage_total = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Maximum total uses (null = unlimited)"
    )
    max_usage_per_user = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        help_text="Maximum uses per user"
    )
    current_usage_count = models.PositiveIntegerField(
        default=0,
        help_text="Current total usage count"
    )

    # User Restrictions
    is_user_specific = models.BooleanField(
        default=False,
        help_text="Whether coupon is restricted to specific users"
    )
    allowed_users = models.ManyToManyField(
        User,
        blank=True,
        related_name="exclusive_coupons",
        help_text="Users who can use this coupon (if user-specific)"
    )

    # Validity Period
    valid_from = models.DateTimeField(
        help_text="Coupon valid from this date/time"
    )
    valid_until = models.DateTimeField(
        help_text="Coupon valid until this date/time"
    )

    # Status
    is_active = models.BooleanField(
        default=True,
        help_text="Whether coupon is active"
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["code"]),
            models.Index(fields=["is_active", "valid_from", "valid_until"]),
        ]

    def __str__(self):
        return f"{self.code} - {self.get_discount_display()}"

    def get_discount_display(self):
        """Return human-readable discount description."""
        if self.discount_type == "percentage":
            return f"{self.discount_value}% off"
        return f"${self.discount_value} off"

    def is_valid(self):
        """Check if coupon is currently valid."""
        now = timezone.now()
        return (
            self.is_active
            and self.valid_from <= now <= self.valid_until
            and (self.max_usage_total is None or self.current_usage_count < self.max_usage_total)
        )

    def can_user_use(self, user):
        """Check if specific user can use this coupon."""
        if not self.is_valid():
            return False, "Coupon is not valid"

        # Check user-specific restriction
        if self.is_user_specific and not self.allowed_users.filter(id=user.id).exists():
            return False, "This coupon is not available for your account"

        # Check per-user usage limit
        user_usage_count = CouponUsage.objects.filter(
            coupon=self,
            user=user
        ).count()

        if user_usage_count >= self.max_usage_per_user:
            return False, f"You have already used this coupon {self.max_usage_per_user} time(s)"

        return True, "Coupon is valid"

    def calculate_discount(self, order_amount):
        """
        Calculate discount amount for given order amount.
        Returns (discount_amount, final_amount).
        """
        if order_amount < self.minimum_order_amount:
            return Decimal("0.00"), order_amount

        if self.discount_type == "percentage":
            discount = (order_amount * self.discount_value / 100).quantize(Decimal("0.01"))

            # Apply maximum discount cap if set
            if self.maximum_discount_amount and discount > self.maximum_discount_amount:
                discount = self.maximum_discount_amount
        else:
            discount = self.discount_value

        # Ensure discount doesn't exceed order amount
        discount = min(discount, order_amount)
        final_amount = order_amount - discount

        return discount, final_amount

    def increment_usage(self):
        """Increment usage counter."""
        self.current_usage_count += 1
        self.save(update_fields=["current_usage_count"])


class CouponUsage(models.Model):
    """
    Track coupon usage by users.

    Business Rules:
    - Records each coupon use
    - Links to order for audit trail
    - Tracks discount amount applied
    """

    coupon = models.ForeignKey(
        Coupon,
        on_delete=models.PROTECT,
        related_name="usages"
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="coupon_usages"
    )
    order_id = models.IntegerField(
        help_text="Order ID where coupon was used"
    )

    # Snapshot of discount at time of use
    order_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Order amount before discount"
    )
    discount_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Discount amount applied"
    )
    final_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Order amount after discount"
    )

    used_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-used_at"]
        indexes = [
            models.Index(fields=["coupon", "user"]),
            models.Index(fields=["user", "-used_at"]),
        ]

    def __str__(self):
        return f"{self.user.username} used {self.coupon.code} on order #{self.order_id}"
