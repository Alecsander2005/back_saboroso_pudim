from decimal import Decimal

from django.db import transaction
from rest_framework import serializers

from products.models import Product, ProductSize
from store.models import StoreSettings

from .models import Order, OrderItem, OrderStatusHistory


class OrderItemSerializer(
    serializers.ModelSerializer
):
    subtotal = serializers.ReadOnlyField()
    

    class Meta:
        model = OrderItem

        fields = [
            "id",
            "product",
            "product_name",
            "size",
            "quantity",
            "price",
            "subtotal",
        ]

        read_only_fields = [
            "id",
            "product_name",
            "size",
            "price",
            "subtotal",
        ]
    
class OrderStatusHistorySerializer(serializers.ModelSerializer):
    changed_by_name = serializers.SerializerMethodField()

    class Meta:

        model = OrderStatusHistory

        fields = [
            "id",
            "status",
            "changed_by",
            "changed_by_name",
            "created_at",
        ]

        read_only_fields = fields

    def get_changed_by_name(self, obj):
        if not obj.changed_by:
            return None

        return obj.changed_by.get_full_name()


class OrderSerializer(
    serializers.ModelSerializer
):
    items = OrderItemSerializer(
        many=True,
        read_only=True
    )

    status_history = OrderStatusHistorySerializer(
        many=True,
        read_only = True
    )

    class Meta:
        model = Order

        fields = [
            "id",
            "user",
            "customer_name",
            "customer_email",
            "customer_whatsapp",
            "delivery_date",
            "delivery_method",
            "address",
            "address_rua",
            "address_bairro",
            "address_numero",
            "address_complemento",
            "address_referencia",
            "delivery_fee",
            "total",
            "status",
            "items",
            "created_at",
            "updated_at",
            "status_history",
        ]

        read_only_fields = [
            "id",
            "user",
            "delivery_fee",
            "total",
            "status",
            "items",
            "created_at",
            "updated_at",
        ]


class OrderCreateItemSerializer(
    serializers.Serializer
):
    product_id = serializers.IntegerField()

    size_id = serializers.IntegerField()

    quantity = serializers.IntegerField(
        min_value=1
    )


class OrderCreateSerializer(
    serializers.ModelSerializer
):
    items = OrderCreateItemSerializer(
        many=True
    )

    class Meta:
        model = Order

        fields = [
            "customer_name",
            "customer_email",
            "customer_whatsapp",
            "delivery_date",
            "delivery_method",
            "address",
            "address_rua",
            "address_bairro",
            "address_numero",
            "address_complemento",
            "address_referencia",
            "items",
        ]

        extra_kwargs = {
            "address": {"required": False, "allow_blank": True, "allow_null": True},
            "address_rua": {"required": False, "allow_blank": True, "allow_null": True},
            "address_bairro": {"required": False, "allow_blank": True, "allow_null": True},
            "address_numero": {"required": False, "allow_blank": True, "allow_null": True},
            "address_complemento": {"required": False, "allow_blank": True, "allow_null": True},
            "address_referencia": {"required": False, "allow_blank": True, "allow_null": True},
            "delivery_date": {"required": False, "allow_null": True},
        }

    def validate_items(self, value):
        if not value:
            raise serializers.ValidationError(
                "O pedido precisa ter pelo menos "
                "um produto."
            )

        return value

    def validate(self, attrs):
        delivery_method = attrs.get(
            "delivery_method"
        )

        if delivery_method == "entrega":

            address = attrs.get("address")
            rua = attrs.get("address_rua")
            bairro = attrs.get("address_bairro")
            numero = attrs.get("address_numero")

            if not address and not (rua and bairro and numero):
                raise serializers.ValidationError({
                    "address": "Informe o endereço para entrega."
                })
        elif delivery_method == "retirada":
            attrs["address"] = ""
            attrs["address_rua"] = ""
            attrs["address_bairro"] = ""
            attrs["address_numero"] = ""
            attrs["address_complemento"] = ""
            attrs["address_referencia"] = ""

        return attrs

    @transaction.atomic
    def create(self, validated_data):

        items_data = validated_data.pop(
            "items"
        )

        order = Order.objects.create(
            **validated_data
        )

        total = Decimal("0.00")

        for item_data in items_data:

            product_id = item_data[
                "product_id"
            ]

            size_id = item_data[
                "size_id"
            ]

            quantity = item_data[
                "quantity"
            ]

            try:
                product = Product.objects.get(
                    id=product_id,
                    is_active=True
                )

            except Product.DoesNotExist:

                raise serializers.ValidationError({
                    "items": (
                        f"Produto {product_id} "
                        "não encontrado."
                    )
                })

            try:
                size = ProductSize.objects.get(
                    id=size_id,
                    product=product,
                    is_active=True
                )

            except ProductSize.DoesNotExist:

                raise serializers.ValidationError({
                    "items": (
                        f"Tamanho {size_id} "
                        "não encontrado para "
                        f"o produto {product_id}."
                    )
                })

            item = OrderItem.objects.create(
                order=order,
                product=product,
                product_name=product.name,
                size=size.label,
                quantity=quantity,
                price=size.price,
            )

            total += item.subtotal
            settings = StoreSettings.objects.first()

        if settings:

            if not settings.loja_aberta:
                raise serializers.ValidationError({
                    "detail": (
                        "A loja está fechada "
                        "no momento."
                    )
                })

            if (
                total < settings.pedido_minimo
            ):
                raise serializers.ValidationError({
                    "detail": (
                        "O pedido não atingiu "
                        "o valor mínimo de "
                        f"R$ {settings.pedido_minimo}."
                    )
                })

        delivery_fee = Decimal("0.00")

        if (
            order.delivery_method
            == "entrega"
        ):
            settings = (
                StoreSettings.objects.first()
            )

            if settings:
                delivery_fee = (
                    settings.taxa_entrega
                )

        total += delivery_fee

        order.delivery_fee = delivery_fee
        order.total = total

        order.save(
            update_fields=[
                "delivery_fee",
                "total",
                "updated_at",
            ]
        )

        OrderStatusHistory.objects.create(
            order = order,
            status = order.status,
            changed_by = order.user
        )

        return order

class OrderAdminUpdateSerializer(
    serializers.ModelSerializer
):

    status = serializers.ChoiceField(choices=Order.STATUS_CHOICES)

    class Meta:
        model = Order

        fields = [
            "status",
        ]

    def validate_status(self, value):
        return value

class OrderStatusUpdateSerializer(serializers.Serializer):
    status = serializers.ChoiceField(
        choices = Order.STATUS_CHOICES
    )

    def validate_status(self, value):
        order = self.context["order"]
        if value == order.status:
            raise serializers.ValidationError(
                f"O status do pedido já está definido como '{order.status}'."
            )
        return value
