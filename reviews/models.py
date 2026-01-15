from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import Avg

User = get_user_model()


class Review(models.Model):
    """
    Customer review for a product.

    Business Rules:
    - User can only review a product once
    - Rating must be between 1-5
    - Review can only be created for purchased products
    - Reviews can be edited within 7 days of creation
    - Admin can moderate/delete inappropriate reviews
    """

    RATING_CHOICES = (
        (1, "1 - Poor"),
        (2, "2 - Fair"),
        (3, "3 - Good"),
        (4, "4 - Very Good"),
        (5, "5 - Excellent"),
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="reviews"
    )
    product_id = models.IntegerField(
        help_text="ID of the product being reviewed"
    )
    order_id = models.IntegerField(
        help_text="Order ID where this product was purchased",
        null=True,
        blank=True
    )

    rating = models.PositiveSmallIntegerField(
        choices=RATING_CHOICES,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Rating from 1 (Poor) to 5 (Excellent)"
    )
    comment = models.TextField(
        blank=True,
        help_text="Optional review comment"
    )

    # Moderation
    is_verified_purchase = models.BooleanField(
        default=False,
        help_text="Whether this review is from a verified purchase"
    )
    is_approved = models.BooleanField(
        default=True,
        help_text="Admin approval status"
    )
    moderation_note = models.TextField(
        blank=True,
        help_text="Internal note for moderation"
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        unique_together = ("user", "product_id")
        indexes = [
            models.Index(fields=["product_id", "-created_at"]),
            models.Index(fields=["user", "-created_at"]),
            models.Index(fields=["is_approved", "-created_at"]),
        ]

    def __str__(self):
        return f"{self.user.username} - Product {self.product_id} - {self.rating}★"

    @staticmethod
    def get_product_average_rating(product_id):
        """Calculate average rating for a specific product."""
        result = Review.objects.filter(
            product_id=product_id,
            is_approved=True
        ).aggregate(avg_rating=Avg("rating"))
        return round(result["avg_rating"], 2) if result["avg_rating"] else None

    @staticmethod
    def get_product_rating_distribution(product_id):
        """Get rating distribution for a product (count per rating)."""
        reviews = Review.objects.filter(
            product_id=product_id,
            is_approved=True
        )

        distribution = {
            "5": reviews.filter(rating=5).count(),
            "4": reviews.filter(rating=4).count(),
            "3": reviews.filter(rating=3).count(),
            "2": reviews.filter(rating=2).count(),
            "1": reviews.filter(rating=1).count(),
        }
        distribution["total"] = sum(distribution.values())
        return distribution


class ReviewHelpfulness(models.Model):
    """
    Track whether users found a review helpful.

    Business Rules:
    - User can only vote once per review
    - User cannot vote on their own reviews
    """

    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name="helpfulness_votes"
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="review_votes"
    )
    is_helpful = models.BooleanField(
        help_text="True if helpful, False if not helpful"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("review", "user")
        verbose_name_plural = "Review helpfulness votes"

    def __str__(self):
        helpful_text = "helpful" if self.is_helpful else "not helpful"
        return f"{self.user.username} found review #{self.review.id} {helpful_text}"
