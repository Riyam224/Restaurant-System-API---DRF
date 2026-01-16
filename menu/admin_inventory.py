"""
Admin configuration for inventory management
"""
from django.contrib import admin
from django.utils.html import format_html
from .models import ProductInventory, InventoryTransaction


@admin.register(ProductInventory)
class ProductInventoryAdmin(admin.ModelAdmin):
    """Admin for product inventory"""

    list_display = (
        "product",
        "quantity_display",
        "low_stock_threshold",
        "stock_status",
        "auto_disable_on_zero",
        "updated_at",
    )

    list_filter = ("auto_disable_on_zero", "updated_at")
    search_fields = ("product__name",)
    readonly_fields = ("created_at", "updated_at")

    fieldsets = (
        ("Product", {
            "fields": ("product",)
        }),
        ("Stock Levels", {
            "fields": ("quantity", "low_stock_threshold")
        }),
        ("Settings", {
            "fields": ("auto_disable_on_zero",)
        }),
        ("Timestamps", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",)
        }),
    )

    def quantity_display(self, obj):
        """Display quantity with color coding"""
        if obj.is_out_of_stock():
            color = "red"
            label = f"{obj.quantity} (OUT OF STOCK)"
        elif obj.is_low_stock():
            color = "orange"
            label = f"{obj.quantity} (LOW STOCK)"
        else:
            color = "green"
            label = str(obj.quantity)

        return format_html(
            '<strong style="color: {};">{}</strong>',
            color,
            label
        )
    quantity_display.short_description = "Quantity"

    def stock_status(self, obj):
        """Display stock status badge"""
        if obj.is_out_of_stock():
            return format_html(
                '<span style="background-color: #dc3545; color: white; '
                'padding: 3px 10px; border-radius: 3px;">OUT OF STOCK</span>'
            )
        elif obj.is_low_stock():
            return format_html(
                '<span style="background-color: #ffc107; color: black; '
                'padding: 3px 10px; border-radius: 3px;">LOW STOCK</span>'
            )
        else:
            return format_html(
                '<span style="background-color: #28a745; color: white; '
                'padding: 3px 10px; border-radius: 3px;">IN STOCK</span>'
            )
    stock_status.short_description = "Status"


@admin.register(InventoryTransaction)
class InventoryTransactionAdmin(admin.ModelAdmin):
    """Admin for inventory transactions"""

    list_display = (
        "created_at",
        "inventory",
        "transaction_type",
        "quantity_change_display",
        "quantity_after",
        "order_id",
    )

    list_filter = ("transaction_type", "created_at")
    search_fields = ("inventory__product__name", "order_id", "notes")
    readonly_fields = (
        "inventory",
        "transaction_type",
        "quantity_change",
        "quantity_after",
        "order_id",
        "created_at",
    )

    fieldsets = (
        ("Transaction Details", {
            "fields": (
                "inventory",
                "transaction_type",
                "quantity_change",
                "quantity_after",
            )
        }),
        ("Related Information", {
            "fields": ("order_id", "notes")
        }),
        ("Timestamp", {
            "fields": ("created_at",)
        }),
    )

    def has_add_permission(self, request):
        """Prevent manual creation"""
        return False

    def has_delete_permission(self, request, obj=None):
        """Prevent deletion (audit trail)"""
        return False

    def quantity_change_display(self, obj):
        """Display quantity change with color"""
        if obj.quantity_change > 0:
            color = "green"
            sign = "+"
        else:
            color = "red"
            sign = ""

        return format_html(
            '<strong style="color: {};">{}{}</strong>',
            color,
            sign,
            obj.quantity_change
        )
    quantity_change_display.short_description = "Change"
