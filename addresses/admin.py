from django.contrib import admin
from .models import Address


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "label", "city", "street", "created_at")
    list_filter = ("city", "created_at")
    search_fields = ("user__username", "user__email", "label", "city", "street")
    readonly_fields = ("created_at",)
    ordering = ("-created_at",)
