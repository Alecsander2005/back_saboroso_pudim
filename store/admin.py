from django.contrib import admin

from .models import StoreSettings


@admin.register(StoreSettings)
class StoreSettingsAdmin(admin.ModelAdmin):
    list_display = (
        "store_name",
        "whatsapp",
        "email",
        "is_open",
        "updated_at",
    )

    search_fields = (
        "store_name",
        "email",
        "whatsapp",
    )

    list_filter = (
        "is_open",
    )