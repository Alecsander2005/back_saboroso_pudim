import json
from datetime import timedelta

from django.db.models import Sum
from django.utils import timezone
from rest_framework import serializers

from orders.models import OrderItem
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

    sizes = ProductSizeSerializer(many=True, read_only=True)
    image_url = serializers.SerializerMethodField()
    is_best_seller = serializers.SerializerMethodField()
    weekly_order_count = serializers.SerializerMethodField()

    def _weekly_ranking(self):
        cache = getattr(self, "_weekly_ranking_cache", None)
        if cache is not None:
            return cache

        now = timezone.now()
        week_start = (now - timedelta(days=now.weekday())).replace(hour=0, minute=0, second=0, microsecond=0)
        week_end = week_start + timedelta(days=7)

        ranking = list(
            OrderItem.objects.filter(
                created_at__gte=week_start,
                created_at__lt=week_end,
                order__status__in=["pendente", "preparando", "pronto", "entregue", "saiu_entrega"],
                product__is_active=True,
            ).values("product_id").annotate(total=Sum("quantity")).order_by("-total", "product_id")[:6]
        )
        cache = {int(row["product_id"]): int(row["total"] or 0) for row in ranking}
        self._weekly_ranking_cache = cache
        return cache

    def get_image_url(self, obj):
        if not obj.image:
            return None
        request = self.context.get("request")
        if request:
            return request.build_absolute_uri(obj.image.url)
        return obj.image.url

    def get_weekly_order_count(self, obj):
        return self._weekly_ranking().get(obj.id, 0)

    def get_is_best_seller(self, obj):
        return obj.id in self._weekly_ranking() and self._weekly_ranking().get(obj.id, 0) > 0


    class Meta:
        model = Product

        fields = [
            "id",
            "name",
            "description",
            "image",
            "image_url",
            "is_active",
            "is_weekly",
            "is_best_seller",
            "weekly_order_count",
            "sizes",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
            "sizes",
            "is_best_seller",
            "weekly_order_count",
        ]

    def _get_sizes(self, attrs):
        raw_sizes = attrs.pop("sizes", None)
        if raw_sizes is None:
            raw_sizes = self.initial_data.get("sizes")
        if isinstance(raw_sizes, str):
            try:
                raw_sizes = json.loads(raw_sizes)
            except json.JSONDecodeError:
                raise serializers.ValidationError({"sizes": "Formato de tamanhos inválido."})
        return raw_sizes if isinstance(raw_sizes, list) else None

    def create(self, validated_data):
        sizes_data = self._get_sizes(validated_data)
        product = super().create(validated_data)
        for size_data in sizes_data or []:
            label = str(size_data.get("label", "")).strip()
            price = size_data.get("price")
            if label and price is not None:
                ProductSize.objects.create(product=product, label=label, price=price)
        return product

    def update(self, instance, validated_data):
        sizes_data = self._get_sizes(validated_data)
        product = super().update(instance, validated_data)
        if sizes_data is not None:
            ProductSize.objects.filter(product=product).delete()
            for size_data in sizes_data:
                label = str(size_data.get("label", "")).strip()
                price = size_data.get("price")
                if label and price is not None:
                    ProductSize.objects.create(product=product, label=label, price=price)
        return product