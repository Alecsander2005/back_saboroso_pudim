from rest_framework import permissions, viewsets
from users.permissions import IsAdminUserType

from .models import StoreSettings
from .serializers import StoreSettingsSerializer


class StoreSettingsViewSet(
    viewsets.ModelViewSet
):
    serializer_class = StoreSettingsSerializer

    queryset = StoreSettings.objects.all()

    def get_permissions(self):
        if self.action in [
            "list",
            "retrieve",
        ]:
            return [
                permissions.AllowAny()
            ]

        return [
                IsAdminUserType()
        ]