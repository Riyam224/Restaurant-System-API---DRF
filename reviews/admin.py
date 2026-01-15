from django.contrib import admin
from .models import Review, ReviewHelpfulness


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "product_id",
        "rating",
        "is_verified_purchase",
        "is_approved",
        "created_at",
    )

    list_filter = (
        "rating",
        "is_verified_purchase",
        "is_approved",
    )

    search_fields = (
        "user__email",
        "product_id",
        "comment",
    )

    readonly_fields = ("created_at", "updated_at")
    ordering = ("-created_at",)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("user")


@admin.register(ReviewHelpfulness)
class ReviewHelpfulnessAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "review",
        "user",
        "is_helpful",
        "created_at",
    )

    list_filter = ("is_helpful", "created_at")
    search_fields = ("review__id", "user__email")
    readonly_fields = ("created_at",)
    ordering = ("-created_at",)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("review", "user")
