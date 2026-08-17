from rest_framework import serializers

from .models import StoreSettings


class StoreSettingsSerializer(
    serializers.ModelSerializer
):
    class Meta:
        model = StoreSettings
        fields = [
            "id",
            "loja_nome",
            "email",
            "telefone",
            "endereco",
            "taxa_entrega",
            "tempo_entrega",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "updated_at",
        ]