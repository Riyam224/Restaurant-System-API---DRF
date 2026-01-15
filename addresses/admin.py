from django.contrib import admin
from .models import Address


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "label", "city", "street", "created_at")
    search_fields = ("user__email", "label", "city", "street")
    list_filter = ("city", "created_at")
