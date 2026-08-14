from decimal import Decimal

from rest_framework import serializers
from django.db import transaction

from products.models import Product, ProductSize

from .models import Order, OrderItem

class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = [
            "id",
            "product",
            "product_name",
            "size_name",
            "quantity",
            "unit_price",
            "subtotal"
        ]
    
class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(
        many = True,
        read_only = True
    )

    class Meta:
        model = Order
        fields = [
            "id",
            "customer_name",
            "customer_email",
            "customer_whatsapp",
            "delivery_method",
            "delivery_date",
            "address",
            "status",
            "total",
            "items",
            "created_at",
            "updated_at"
        ]

class OrderCreateItemSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    size_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value = 1)

class OrderCreateSerializer(serializers.Serializer):
    items = OrderCreateItemSerializer(
        many = True,
        write_only = True
        )

    class Meta:
        model = Order
        fileds =[
            "customer_name",
            "customer_email",
            "customer_whatsapp",
            "delivery_method",
            "delivery_date",
            "address",
            "items",
        ]

    @transaction.atomic
    def create(self, validated_data):
        items_data = validated_data.pop("items")

        order = Order.objects.create(
            **validated_data,
            total = Decimal ("0.00")
        )

        total = Decimal("0.00")

        for item_data in items_data:
            product_id = item_data["product_id"]
            size_id = item_data["size_id"]
            quantity = item_data["quantity"]

            try:
                product = Product.objects.get(
                    id=product_id,
                    is_active=True,
                )
            except Product.DoesNotExist:
                raise serializers.ValidationError(
                    f"Produto {product_id} não encontrado."
                )

            try:
                size = ProductSize.objects.get(
                    id=size_id,
                    product=product,
                    is_active=True,
                )
            except ProductSize.DoesNotExist:
                raise serializers.ValidationError(
                    f"Tamanho {size_id} não encontrado para o produto."
                )

            unit_price = size.price
            subtotal = unit_price * quantity

            OrderItem.objects.create(
                order=order,
                product=product,
                product_name = product.name,
                size_name=size.name,
                quantity=quantity,
                unit_price=unit_price,
                subtotal=subtotal
            )

            total += subtotal

            order.total = total

            order.save(
                update_fields=["total", "updated_at"]
            )

            return order

