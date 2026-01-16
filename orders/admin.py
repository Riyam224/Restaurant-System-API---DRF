from django.contrib import admin
from .models import Order, OrderItem, OrderStatusHistory


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("product_id", "product_name", "price", "quantity")
    can_delete = False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "total_price",
        "status",
        "payment_status",
        "created_at",
    )
    list_filter = ("status", "payment_status", "created_at")
    search_fields = ("id", "user__email")

    readonly_fields = (
        "user",
        "address",
        "subtotal",
        "discount_amount",
        "total_price",
        "coupon_code",
        "payment_status",
        "created_at",
        "updated_at",
    )

    # Allow admins to only update the order status
    fields = (
        "user",
        "address",
        "status",  # ← Only editable field
        "payment_status",
        "subtotal",
        "discount_amount",
        "coupon_code",
        "total_price",
        "created_at",
        "updated_at",
    )
    inlines = [OrderItemInline]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related("user", "address")

    # 🚫 Disable manual creation
    def has_add_permission(self, request):
        return False


@admin.register(OrderStatusHistory)
class OrderStatusHistoryAdmin(admin.ModelAdmin):
    list_display = ("order", "status", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("order__id",)
    readonly_fields = ("order", "status", "created_at", "updated_at")

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
