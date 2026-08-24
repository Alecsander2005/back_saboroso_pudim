from django.contrib import admin

from .models import StoreSettings


@admin.register(StoreSettings)
class StoreSettingsAdmin(admin.ModelAdmin):

    list_display = [
        "name",
        "taxa_entrega",
        "pedido_minimo",
        "loja_aberta",
        "updated_at",
    ]

    list_filter = [
        "loja_aberta",
    ]

    search_fields = [
        "name",
        "phone",
        "whatsapp",
    ]