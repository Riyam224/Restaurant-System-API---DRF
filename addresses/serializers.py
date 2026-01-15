from rest_framework import serializers
from .models import Address


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = [
            "id",
            "label",
            "city",
            "street",
            "building",
            "lat",
            "lng",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]

    def validate_label(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Label cannot be empty.")
        return value.strip()

    def validate_city(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("City cannot be empty.")
        return value.strip()

    def validate_street(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Street cannot be empty.")
        return value.strip()


class AddressDetailSerializer(serializers.ModelSerializer):
    """Read-only serializer for displaying address details in orders."""

    class Meta:
        model = Address
        fields = [
            "id",
            "label",
            "city",
            "street",
            "building",
        ]
        read_only_fields = fields
