from decimal import Decimal
from rest_framework import serializers
from .models import Order, OrderItem, OrderStatusHistory


class OrderItemSerializer(serializers.ModelSerializer):
    subtotal = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = [
            "id",
            "product_id",
            "product_name",
            "price",
            "quantity",
            "subtotal",
        ]

    def get_subtotal(self, obj) -> Decimal:
        return obj.subtotal()


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    history = serializers.SerializerMethodField()
    status_display = serializers.CharField(source="get_status_display", read_only=True)

    def get_history(self, obj):
        request = self.context.get("request")
        if request and not request.user.is_staff and obj.user != request.user:
            return []
        queryset = obj.history.order_by("created_at")
        return OrderStatusHistorySerializer(queryset, many=True).data

    class Meta:
        model = Order
        fields = [
            "id",
            "address",
            "status",
            "status_display",
            "total_price",
            "created_at",
            "updated_at",
            "items",
            "history",
        ]


class OrderStatusHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderStatusHistory
        fields = ["id", "status", "created_at"]
