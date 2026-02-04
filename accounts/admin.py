from django.contrib import admin
from .models import PasswordResetOTP
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

User = get_user_model()


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ["username", "email", "role", "is_verified", "is_staff", "is_active"]
    list_filter = ["role", "is_verified", "is_staff", "is_active", "date_joined"]
    search_fields = ["username", "email", "phone"]
    ordering = ["-date_joined"]

    fieldsets = BaseUserAdmin.fieldsets + (
        ("Additional Info", {"fields": ("phone", "avatar", "role", "is_verified")}),
    )

    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ("Additional Info", {"fields": ("phone", "avatar", "role", "is_verified")}),
    )


@admin.register(PasswordResetOTP)
class PasswordResetOTPAdmin(admin.ModelAdmin):
    list_display = ["user", "otp", "created_at", "expires_at", "is_used"]
    list_filter = ["is_used", "created_at"]
    search_fields = ["user__email", "user__username", "otp"]
    readonly_fields = ["created_at"]
    ordering = ["-created_at"]
