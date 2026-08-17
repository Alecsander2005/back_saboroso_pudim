from django.contrib import admin

from .models import StoreSettings


@admin.register(StoreSettings)
class StoreSettingsAdmin(admin.ModelAdmin):
    list_display = (
        "loja_nome",
        "email",
        "telefone",
        "taxa_entrega",
        "tempo_entrega",
        "updated_at",
    )

    readonly_fields = (
        "updated_at",
    )

    def has_add_permission(self, request):
        return not StoreSettings.objects.exists()