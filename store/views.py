from rest_framework import (
    permissions,
    status,
    viewsets,
)
from rest_framework.response import Response
from rest_framework.decorators import action

from users.permissions import IsAdminUserType

from .models import StoreSettings
from .serializers import StoreSettingsSerializer


class StoreSettingsViewSet(
    viewsets.ViewSet
):

    def get_permissions(self):

        if self.action in (
            "list",
            "retrieve",
        ):
            return [
                permissions.AllowAny()
            ]

        return [
            IsAdminUserType()
        ]

    def list(self, request):

        settings = (
            StoreSettings.objects.first()
        )

        if not settings:
            return Response({
                "detail": (
                    "As configurações da loja "
                    "ainda não foram cadastradas."
                )
            })

        serializer = StoreSettingsSerializer(
            settings
        )

        return Response(
            serializer.data
        )

    def retrieve(
        self,
        request,
        pk=None
    ):

        settings = (
            StoreSettings.objects.first()
        )

        if not settings:
            return Response(
                {
                    "detail": (
                        "Configurações da loja "
                        "não encontradas."
                    )
                },
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = StoreSettingsSerializer(
            settings
        )

        return Response(
            serializer.data
        )

    @action(detail=False, methods=["patch"], url_path="current", permission_classes=[IsAdminUserType])
    def current(self, request):
        settings = StoreSettings.objects.first()
        if not settings:
            settings = StoreSettings.objects.create()
        serializer = StoreSettingsSerializer(settings, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def create(self, request):

        if StoreSettings.objects.exists():

            return Response(
                {
                    "detail": (
                        "As configurações da loja "
                        "já existem."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = StoreSettingsSerializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        serializer.save()

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )

    def update(
        self,
        request,
        pk=None
    ):

        settings = (
            StoreSettings.objects.first()
        )

        if not settings:
            return Response(
                {
                    "detail": (
                        "Configurações da loja "
                        "não encontradas."
                    )
                },
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = StoreSettingsSerializer(
            settings,
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        serializer.save()

        return Response(
            serializer.data
        )

    def partial_update(
        self,
        request,
        pk=None
    ):

        settings = (
            StoreSettings.objects.first()
        )

        if not settings:
            return Response(
                {
                    "detail": (
                        "Configurações da loja "
                        "não encontradas."
                    )
                },
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = StoreSettingsSerializer(
            settings,
            data=request.data,
            partial=True
        )

        serializer.is_valid(
            raise_exception=True
        )

        serializer.save()

        return Response(
            serializer.data
        )

    def destroy(
        self,
        request,
        pk=None
    ):

        settings = (
            StoreSettings.objects.first()
        )

        if not settings:
            return Response(
                status=status.HTTP_404_NOT_FOUND
            )

        settings.delete()

        return Response(
            status=status.HTTP_204_NO_CONTENT
        )