from rest_framework import serializers
from .models import Category, Product


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "image", "is_active"]


class ProductSerializer(serializers.ModelSerializer):
    category_id = serializers.IntegerField(source="category.id", read_only=True)

    class Meta:
        model = Product
        fields = [
            "id",
            "category_id",
            "name",
            "description",
            "price",
            "image",
            "is_available",
        ]
