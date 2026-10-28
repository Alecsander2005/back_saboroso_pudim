from rest_framework import (
    permissions,
    status,
    viewsets,
)
from rest_framework.decorators import action
from rest_framework.response import Response

from users.permissions import IsAdminUserType

from .models import Order, OrderStatusHistory
from .serializers import (
    OrderCreateSerializer,
    OrderSerializer,
    OrderAdminUpdateSerializer,
    OrderStatusHistorySerializer,
    OrderStatusUpdateSerializer
)  


class OrderViewSet(
    viewsets.ModelViewSet
):

    queryset = (
        Order.objects
        .prefetch_related("items", "status_history")
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
                permissions.AllowAny()
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

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        response_serializer = OrderSerializer(
            serializer.instance,
            context=self.get_serializer_context(),
        )
        return Response(
            response_serializer.data,
            status=status.HTTP_201_CREATED,
        )

    def get_queryset(self):

        queryset = super().get_queryset()
        user = self.request.user

        if user.is_authenticated and user.tipo_usuario == "admin":
            return queryset

        if user.is_authenticated:
            return queryset.filter(user=user)

        return queryset.none()

    def perform_create(self, serializer):
        user = self.request.user if self.request.user.is_authenticated else None
        serializer.save(user=user)
    
    @action( detail = True, methods= ["patch"], url_path = "status")
    def update_status(self,request,pk=None):
        order = self.get_object()

        serializer = OrderStatusUpdateSerializer(
            data = request.data,
            context= {
                "order": order
            }
        )

        serializer.is_valid(
            raise_exception = True
        )

        new_status = serializer.validated_data["status"]

        order.status = new_status
        order.save(update_fields=["status", "updated_at"])

        OrderStatusHistory.objects.create(
            order=order,
            status=new_status,
            changed_by=request.user,
        )

        return Response(
            OrderSerializer(order, context={"request": request}).data
        )
    
    @action( detail = True, methods=["post"], url_path = "cancel")
    def cancel(self,request,pk=None):
        order = self.get_object()

        allowed_statuses = [
            "pendente",
            "confirmado"
        ]

        if order.status not in allowed_statuses:
            return Response(
                {
                    "detail":(
                        "este pedido não pode "
                        "mais ser cancelado."
                    )
                },
                status = 400
            )

        order.status = "cancelado"

        order.save(
            update_fields =[
                "status",
                "updated_at"
            ]
        )

        OrderStatusHistory.objects.create(
            order=order,
            status="cancelado",
            changed_by=request.user,
        )

        return Response(
            OrderSerializer(order, context={"request": request}).data
        )