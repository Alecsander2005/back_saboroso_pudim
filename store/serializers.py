from rest_framework import serializers

from .models import StoreSettings


class StoreSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = StoreSettings
        fields = [
            "id",
            "store_name",
            "description",
            "whatsapp",
            "email",
            "address",
            "logo",
            "is_open",
            "created_at",
            "updated_at",
        ]