from rest_framework import serializers

from .models import StoreSettings


class StoreSettingsSerializer(
    serializers.ModelSerializer
):

    class Meta:
        model = StoreSettings

        fields = [
            "id",
            "name",
            "phone",
            "whatsapp",
            "address",
            "taxa_entrega",
            "pedido_minimo",
            "loja_aberta",
            "horario_abertura",
            "horario_fechamento",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "updated_at",
        ]

    def validate_taxa_entrega(self, value):

        if value < 0:
            raise serializers.ValidationError(
                "A taxa de entrega não pode ser negativa."
            )

        return value

    def validate_pedido_minimo(self, value):

        if value < 0:
            raise serializers.ValidationError(
                "O pedido mínimo não pode ser negativo."
            )

        return value