from django.contrib import admin
from .models import PasswordResetOTP
from django.contrib.auth import get_user_model

User = get_user_model()


@admin.register(PasswordResetOTP)
class PasswordResetOTPAdmin(admin.ModelAdmin):
    list_display = ["user", "otp", "created_at", "expires_at", "is_used"]
    list_filter = ["is_used", "created_at"]
    search_fields = ["user__email", "user__username", "otp"]
    readonly_fields = ["created_at"]
    ordering = ["-created_at"]
