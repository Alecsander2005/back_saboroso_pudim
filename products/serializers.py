from rest_framework import serializers

from .models import Product, ProductSize


class ProductSizeSerializer(
    serializers.ModelSerializer
):

    class Meta:
        model = ProductSize

        fields = [
            "id",
            "label",
            "price",
            "is_active",
        ]

        read_only_fields = [
            "id",
        ]

    def validate_price(self, value):

        if value < 0:
            raise serializers.ValidationError(
                "O preço não pode ser negativo."
            )

        return value


class ProductSerializer(
    serializers.ModelSerializer
):

    sizes = ProductSizeSerializer(
        many=True,
        read_only=True
    )

    class Meta:
        model = Product

        fields = [
            "id",
            "name",
            "description",
            "image",
            "is_active",
            "sizes",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
            "sizes",
        ]