from django.contrib import admin
from .models import Coupon, CouponUsage


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = (
        "code",
        "discount_type",
        "discount_value",
        "minimum_order_amount",
        "current_usage_count",
        "max_usage_total",
        "valid_from",
        "valid_until",
        "is_active",
    )
    list_filter = (
        "discount_type",
        "is_active",
        "is_user_specific",
        "valid_from",
        "valid_until",
    )
    search_fields = ("code", "description")
    readonly_fields = ("current_usage_count", "created_at", "updated_at")
    ordering = ("-created_at",)
    filter_horizontal = ("allowed_users",)

    fieldsets = (
        ("Basic Information", {
            "fields": ("code", "description", "is_active")
        }),
        ("Discount Configuration", {
            "fields": (
                "discount_type",
                "discount_value",
                "minimum_order_amount",
                "maximum_discount_amount"
            )
        }),
        ("Usage Limits", {
            "fields": (
                "max_usage_total",
                "max_usage_per_user",
                "current_usage_count"
            )
        }),
        ("User Restrictions", {
            "fields": ("is_user_specific", "allowed_users"),
            "classes": ("collapse",),
        }),
        ("Validity Period", {
            "fields": ("valid_from", "valid_until")
        }),
        ("Timestamps", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",),
        }),
    )


@admin.register(CouponUsage)
class CouponUsageAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "coupon",
        "user",
        "order_id",
        "discount_amount",
        "used_at",
    )
    list_filter = ("used_at",)
    search_fields = (
        "coupon__code",
        "user__email",
        "order_id",
    )
    readonly_fields = (
        "coupon",
        "user",
        "order_id",
        "order_amount",
        "discount_amount",
        "final_amount",
        "used_at",
    )
    ordering = ("-used_at",)

    def has_add_permission(self, request):
        """Prevent manual creation of coupon usages."""
        return False

    def has_change_permission(self, request, obj=None):
        """Make coupon usages read-only."""
        return False

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("coupon", "user")
