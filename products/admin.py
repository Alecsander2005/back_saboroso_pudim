from django.contrib import admin

from .models import Product, ProductSize


class ProductSizeInline(admin.TabularInline):
    model = ProductSize
    extra = 1


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "is_active",
        "is_weekly",
    )

    list_filter = (
        "is_active",
        "is_weekly",
    )

    fieldsets = (
        (None, {"fields": ("name", "description", "image", "is_active", "is_weekly")}),
        ("Tamanhos", {"classes": ("collapse",), "fields": ()}),
    )

    search_fields = (
        "name",
        "description",
    )

    inlines = [
        ProductSizeInline,
    ]


@admin.register(ProductSize)
class ProductSizeAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "product",
        "label",
        "price",
        "is_active",
    )

    list_filter = (
        "is_active",
    )

    search_fields = (
        "product__name",
        "label",
    )