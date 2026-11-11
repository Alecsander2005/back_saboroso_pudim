
from rest_framework import permissions, viewsets

from users.permissions import IsAdminUserType

from .models import Product, ProductSize
from .serializers import ProductSerializer, ProductSizeSerializer


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.prefetch_related("sizes")
    serializer_class = ProductSerializer

    def get_permissions(self):
        if self.action in ("list", "retrieve"):
            return [permissions.AllowAny()]

        return [IsAdminUserType()]

    def get_queryset(self):
        queryset = super().get_queryset()

        if (
            self.request.user.is_authenticated
            and self.request.user.tipo_usuario == "admin"
        ):
            return queryset

        return queryset.filter(is_active=True)


class ProductSizeViewSet(viewsets.ModelViewSet):
    queryset = ProductSize.objects.select_related("product")
    serializer_class = ProductSizeSerializer

    def get_permissions(self):
        if self.action in ("list", "retrieve"):
            return [permissions.AllowAny()]

        return [IsAdminUserType()]

    def get_queryset(self):
        queryset = super().get_queryset()

        product_id = self.request.query_params.get("product")

        if product_id:
            queryset = queryset.filter(product_id=product_id)

        if (
            not self.request.user.is_authenticated
            or self.request.user.tipo_usuario != "admin"
        ):
            queryset = queryset.filter(
                is_active=True,
                product__is_active=True,
            )

        return queryset
