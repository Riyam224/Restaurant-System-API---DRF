from rest_framework import serializers
from django.utils import timezone
from datetime import timedelta
from drf_spectacular.utils import extend_schema_field
from .models import Review, ReviewHelpfulness


class ReviewSerializer(serializers.ModelSerializer):
    """Serializer for listing and retrieving reviews."""

    username = serializers.CharField(source="user.username", read_only=True)
    helpful_count = serializers.SerializerMethodField()
    not_helpful_count = serializers.SerializerMethodField()
    can_edit = serializers.SerializerMethodField()
    rating_display = serializers.CharField(source="get_rating_display", read_only=True)

    class Meta:
        model = Review
        fields = [
            "id",
            "user",
            "username",
            "product_id",
            "order_id",
            "rating",
            "rating_display",
            "comment",
            "is_verified_purchase",
            "is_approved",
            "helpful_count",
            "not_helpful_count",
            "can_edit",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "user",
            "username",
            "is_verified_purchase",
            "is_approved",
            "created_at",
            "updated_at",
        ]

    @extend_schema_field(serializers.IntegerField)
    def get_helpful_count(self, obj) -> int:
        """Count of users who found this review helpful."""
        return obj.helpfulness_votes.filter(is_helpful=True).count()

    @extend_schema_field(serializers.IntegerField)
    def get_not_helpful_count(self, obj) -> int:
        """Count of users who found this review not helpful."""
        return obj.helpfulness_votes.filter(is_helpful=False).count()

    @extend_schema_field(serializers.BooleanField)
    def get_can_edit(self, obj) -> bool:
        """Check if user can edit this review (within 7 days)."""
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            return False

        is_owner = obj.user == request.user
        within_edit_window = timezone.now() - obj.created_at < timedelta(days=7)

        return is_owner and within_edit_window


class ReviewCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating reviews."""

    class Meta:
        model = Review
        fields = [
            "product_id",
            "order_id",
            "rating",
            "comment",
        ]

    def validate_rating(self, value):
        """Ensure rating is between 1-5."""
        if not 1 <= value <= 5:
            raise serializers.ValidationError("Rating must be between 1 and 5.")
        return value

    def validate_comment(self, value):
        """Validate and clean comment."""
        if value:
            value = value.strip()
            if len(value) < 10:
                raise serializers.ValidationError(
                    "Comment must be at least 10 characters long."
                )
            if len(value) > 1000:
                raise serializers.ValidationError(
                    "Comment cannot exceed 1000 characters."
                )
        return value

    def validate(self, attrs):
        """Validate that user hasn't already reviewed this product."""
        request = self.context.get("request")
        if not request:
            raise serializers.ValidationError("Request context is required.")

        user = request.user
        product_id = attrs.get("product_id")

        # Check for existing review
        existing_review = Review.objects.filter(
            user=user,
            product_id=product_id
        ).first()

        if existing_review:
            raise serializers.ValidationError(
                "You have already reviewed this product. "
                "You can update your existing review instead."
            )

        return attrs

    def create(self, validated_data):
        """Create review with user from request context."""
        request = self.context.get("request")
        validated_data["user"] = request.user

        # TODO: Verify if user actually purchased this product
        # For now, set is_verified_purchase based on whether order_id is provided
        validated_data["is_verified_purchase"] = bool(validated_data.get("order_id"))

        return super().create(validated_data)


class ReviewUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating reviews."""

    class Meta:
        model = Review
        fields = ["rating", "comment"]

    def validate_rating(self, value):
        """Ensure rating is between 1-5."""
        if not 1 <= value <= 5:
            raise serializers.ValidationError("Rating must be between 1 and 5.")
        return value

    def validate_comment(self, value):
        """Validate and clean comment."""
        if value:
            value = value.strip()
            if len(value) < 10:
                raise serializers.ValidationError(
                    "Comment must be at least 10 characters long."
                )
            if len(value) > 1000:
                raise serializers.ValidationError(
                    "Comment cannot exceed 1000 characters."
                )
        return value

    def validate(self, attrs):
        """Ensure user can still edit (within 7 days)."""
        review = self.instance
        time_since_creation = timezone.now() - review.created_at

        if time_since_creation > timedelta(days=7):
            raise serializers.ValidationError(
                "Reviews can only be edited within 7 days of creation."
            )

        return attrs


class ReviewHelpfulnessSerializer(serializers.ModelSerializer):
    """Serializer for marking reviews as helpful/not helpful."""

    class Meta:
        model = ReviewHelpfulness
        fields = ["id", "review", "is_helpful", "created_at"]
        read_only_fields = ["id", "created_at"]

    def validate(self, attrs):
        """Validate helpfulness vote."""
        request = self.context.get("request")
        if not request:
            raise serializers.ValidationError("Request context is required.")

        user = request.user
        review = attrs.get("review")

        # User cannot vote on their own review
        if review.user == user:
            raise serializers.ValidationError(
                "You cannot vote on your own review."
            )

        # Check if user already voted
        existing_vote = ReviewHelpfulness.objects.filter(
            review=review,
            user=user
        ).first()

        if existing_vote:
            raise serializers.ValidationError(
                "You have already voted on this review."
            )

        return attrs

    def create(self, validated_data):
        """Create helpfulness vote with user from request."""
        request = self.context.get("request")
        validated_data["user"] = request.user
        return super().create(validated_data)


class ProductRatingStatsSerializer(serializers.Serializer):
    """Serializer for product rating statistics."""

    average_rating = serializers.DecimalField(
        max_digits=3,
        decimal_places=2,
        allow_null=True
    )
    total_reviews = serializers.IntegerField()
    rating_distribution = serializers.DictField(
        child=serializers.IntegerField()
    )
