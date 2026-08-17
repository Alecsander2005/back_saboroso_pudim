from rest_framework import permissions, viewsets
from rest_framework.parsers import (
    JSONParser,
    FormParser,
    MultiPartParser,
)

from .models import Product
from .serializers import ProductSerializer


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.prefetch_related(
        "sizes"
    ).all()

    serializer_class = ProductSerializer

    parser_classes = [
        JSONParser,
        MultiPartParser,
        FormParser,
    ]

    def get_permissions(self):
        if self.action in (
            "list",
            "retrieve",
        ):
            return [
                permissions.AllowAny()
            ]

        return [
            permissions.IsAdminUser()
        ]