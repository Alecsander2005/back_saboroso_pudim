from rest_framework import (
    permissions,
    viewsets,
)

from users.permissions import IsAdminUserType

from .models import Order
from .serializers import (
    OrderCreateSerializer,
    OrderSerializer,
    OrderAdminUpdateSerializer
)


class OrderViewSet(
    viewsets.ModelViewSet
):

    queryset = (
        Order.objects
        .prefetch_related("items")
        .select_related("user")
    )

    def get_serializer_class(self):

        if self.action == "create":
            return OrderCreateSerializer

        if self.action in (
            "update",
            "partial_update",
        ):
            return OrderAdminUpdateSerializer

        return OrderSerializer

    def get_permissions(self):

        if self.action == "create":
            return [
                permissions.IsAuthenticated()
            ]

        if self.action in (
            "list",
            "retrieve",
        ):
            return [
                permissions.IsAuthenticated()
            ]

        return [
            IsAdminUserType()
        ]

    def get_queryset(self):

        queryset = super().get_queryset()

        user = self.request.user

        if user.tipo_usuario == "admin":
            return queryset

        return queryset.filter(
            user=user
        )

    def perform_create(
        self,
        serializer
    ):
        serializer.save(
            user=self.request.user
        )