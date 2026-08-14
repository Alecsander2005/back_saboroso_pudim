from rest_framework import serializers

from .models import Product, ProductSize

class ProductSizeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductSize
        field =[
            "id",
            "name",
            "price",
            "is_active",
        ]

class ProductSerializer(serializers.ModelSerializer):
    sizes = ProductSizeSerializer(
        many = True,
        read_only = True,
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
    
        
