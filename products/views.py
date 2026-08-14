from rest_framework import permissions, viewsets

from .models import Product
from .serializers import ProductSerializer


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.prefetch_related(
        "sizes"
    ).all()

    serializer_class = ProductSerializer

    def get_permissions(self):
        if self.action in [
            "list",
            "retrieve",
        ]:
            return [
                permissions.AllowAny()
            ]

        return [
            permissions.IsAdminUser()
        ]