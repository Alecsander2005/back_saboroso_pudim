from django.contrib.auth import authenticate
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User


class UserSerializer(
    serializers.ModelSerializer
):
    class Meta:
        model = User

        fields = [
            "id",
            "email",
            "nome_completo",
            "telefone",
            "tipo_usuario",
            "is_active",
            "is_staff",
            "is_superuser",
            "date_joined",
        ]

        read_only_fields = [
            "id",
            "tipo_usuario",
            "is_active",
            "is_staff",
            "is_superuser",
            "date_joined",
        ]


class RegisterSerializer(
    serializers.ModelSerializer
):
    password = serializers.CharField(
        write_only=True,
        min_length=6
    )

    password_confirm = serializers.CharField(
        write_only=True
    )

    class Meta:
        model = User

        fields = [
            "email",
            "nome_completo",
            "telefone",
            "password",
            "password_confirm",
        ]

    def validate_email(self, value):
        value = value.lower().strip()

        if User.objects.filter(
            email=value
        ).exists():
            raise serializers.ValidationError(
                "Este e-mail já está cadastrado."
            )

        return value

    def validate(self, attrs):
        if attrs["password"] != attrs[
            "password_confirm"
        ]:
            raise serializers.ValidationError({
                "password_confirm": (
                    "As senhas não coincidem."
                )
            })

        return attrs

    def create(self, validated_data):
        validated_data.pop(
            "password_confirm"
        )

        password = validated_data.pop(
            "password"
        )

        user = User.objects.create_user(
            password=password,
            **validated_data
        )

        return user


class LoginSerializer(
    serializers.Serializer
):
    email = serializers.EmailField()
    password = serializers.CharField(
        write_only=True
    )

    def validate(self, attrs):
        email = attrs[
            "email"
        ].lower().strip()

        password = attrs[
            "password"
        ]

        user = authenticate(
            email=email,
            password=password
        )

        if not user:
            raise serializers.ValidationError(
                "E-mail ou senha inválidos."
            )

        if not user.is_active:
            raise serializers.ValidationError(
                "Este usuário está desativado."
            )

        attrs["user"] = user

        return attrs

class AdminUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6, required=False)

    class Meta:
        model = User
        fields = [
            "id", "email", "nome_completo", "telefone", "tipo_usuario",
            "password", "is_active", "is_staff", "is_superuser", "date_joined",
        ]
        read_only_fields = ["id", "is_staff", "is_superuser", "date_joined"]

    def validate_email(self, value):
        return value.lower().strip()

    def create(self, validated_data):
        password = validated_data.pop("password", None)
        if not password:
            raise serializers.ValidationError({"password": "Senha obrigatória."})
        return User.objects.create_user(password=password, **validated_data)

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        for field, value in validated_data.items():
            setattr(instance, field, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()

    def validate(self, attrs):
        self.token = attrs["refresh"]
        return attrs


    def save(self, **kwargs):
        try:
            token = RefreshToken(self.token)

            token.blacklist()

        except Exception :
            raise serializers.ValidationError({
                "refresh": (
                    "refresh token invalido"
                    "ou já revogado"
                )
            })