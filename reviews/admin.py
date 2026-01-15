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
        "created_at",
    )
    search_fields = (
        "user__username",
        "user__email",
        "product_id",
        "comment",
    )
    readonly_fields = ("created_at", "updated_at")
    ordering = ("-created_at",)

    fieldsets = (
        ("Review Information", {
            "fields": ("user", "product_id", "order_id", "rating", "comment")
        }),
        ("Moderation", {
            "fields": ("is_verified_purchase", "is_approved", "moderation_note")
        }),
        ("Timestamps", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",),
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("user")


@admin.register(ReviewHelpfulness)
class ReviewHelpfulnessAdmin(admin.ModelAdmin):
    list_display = ("id", "review", "user", "is_helpful", "created_at")
    list_filter = ("is_helpful", "created_at")
    search_fields = ("review__id", "user__username")
    readonly_fields = ("created_at",)
    ordering = ("-created_at",)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("review", "user")
