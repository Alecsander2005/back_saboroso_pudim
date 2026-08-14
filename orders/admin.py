from django.contrib import admin

from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0

    readonly_fields = (
        "product_name",
        "size_name",
        "quantity",
        "unit_price",
        "subtotal",
    )


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "customer_name",
        "customer_whatsapp",
        "delivery_method",
        "status",
        "total",
        "created_at",
    )

    list_filter = (
        "status",
        "delivery_method",
    )

    search_fields = (
        "customer_name",
        "customer_email",
        "customer_whatsapp",
    )

    readonly_fields = (
        "total",
        "created_at",
        "updated_at",
    )

    inlines = [
        OrderItemInline,
    ]


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "order",
        "product_name",
        "size_name",
        "quantity",
        "unit_price",
        "subtotal",
    )

    search_fields = (
        "product_name",
        "order__customer_name",
    )