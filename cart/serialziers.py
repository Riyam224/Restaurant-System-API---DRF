from decimal import Decimal
from rest_framework import serializers
from .models import Cart, CartItem
from menu.serializers import ProductSerializer


class CartItemSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField(source="product.id")
    name = serializers.CharField(source="product.name")
    price = serializers.DecimalField(max_digits=10, decimal_places=2)
    subtotal = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = ["id", "product_id", "name", "price", "quantity", "subtotal"]

    def get_subtotal(self, obj) -> Decimal:
        return obj.subtotal()


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True)
    total_items = serializers.SerializerMethodField()
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ["id", "items", "total_items", "total_price"]

    def get_total_items(self, obj) -> int:
        return obj.total_items()

    def get_total_price(self, obj) -> Decimal:
        return obj.total_price()
