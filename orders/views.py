from rest_framework import permissions, status, viewsets
from rest_framework.response import Response

from .models import Order
from .serializers import (
    OrderCreateSerializer,
    OrderSerializer,
)


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.prefetch_related(
        "items"
    ).all()

    def get_serializer_class(self):
        if self.action == "create":
            return OrderCreateSerializer

        return OrderSerializer

    def get_permissions(self):
        if self.action == "create":
            return [
                permissions.AllowAny()
            ]

        return [
            permissions.IsAdminUser()
        ]

    def create(
        self,
        request,
        *args,
        **kwargs
    ):
        serializer = self.get_serializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        order = serializer.save()

        response_serializer = OrderSerializer(
            order
        )

        return Response(
            response_serializer.data,
            status=status.HTTP_201_CREATED
        )