from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import StoreSettings
from .serializers import StoreSettingsSerializer


class StoreSettingsViewSet(viewsets.ModelViewSet):
    queryset = StoreSettings.objects.all()
    serializer_class = StoreSettingsSerializer

    def get_permissions(self):
        if self.action in [
            "list",
            "retrieve",
            "current",
        ]:
            return [
                permissions.AllowAny()
            ]

        return [
            permissions.IsAdminUser()
        ]

    @action(
        detail=False,
        methods=["get"],
        url_path="current",
    )
    def current(self, request):
        settings = StoreSettings.objects.first()

        if not settings:
            return Response(
                {
                    "detail": (
                        "Configurações da loja "
                        "não encontradas."
                    )
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = self.get_serializer(
            settings
        )

        return Response(
            serializer.data
        )