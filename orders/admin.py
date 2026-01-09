from django.contrib import admin
from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    readonly_fields = ("subtotal",)
    extra = 0

    def subtotal(self, obj):
        return obj.subtotal()


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "total_price", "status", "created_at")
    readonly_fields = ("total_price", "created_at")
    list_filter = ("status", "created_at")
    inlines = [OrderItemInline]
