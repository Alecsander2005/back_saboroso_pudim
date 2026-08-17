import json

from django.db import transaction
from rest_framework import serializers

from .models import Product, ProductSize


class ProductSizeSerializer(serializers.ModelSerializer):
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


class ProductSerializer(serializers.ModelSerializer):
    sizes = ProductSizeSerializer(
        many=True,
        required=False,
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
        ]

    def to_internal_value(self, data):
        data = data.copy()

        sizes = data.get("sizes")

        if isinstance(sizes, str):
            try:
                data["sizes"] = json.loads(sizes)
            except json.JSONDecodeError:
                raise serializers.ValidationError({
                    "sizes": (
                        "O campo sizes deve conter "
                        "um JSON válido."
                    )
                })

        return super().to_internal_value(data)

    @transaction.atomic
    def create(self, validated_data):
        sizes_data = validated_data.pop(
            "sizes",
            []
        )

        product = Product.objects.create(
            **validated_data
        )

        for size_data in sizes_data:
            ProductSize.objects.create(
                product=product,
                **size_data
            )

        return product

    @transaction.atomic
    def update(
        self,
        instance,
        validated_data
    ):
        sizes_data = validated_data.pop(
            "sizes",
            None
        )

        for attribute, value in validated_data.items():
            setattr(
                instance,
                attribute,
                value
            )

        instance.save()

        if sizes_data is not None:
            instance.sizes.all().delete()

            for size_data in sizes_data:
                ProductSize.objects.create(
                    product=instance,
                    **size_data
                )

        return instance