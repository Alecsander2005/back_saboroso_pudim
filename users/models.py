from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from .managers import UserManager


class User(AbstractBaseUser, PermissionsMixin):

    USER_TYPE_CHOICES = [
        (
            "cliente",
            "Cliente"
        ),
        (
            "admin",
            "Administrador"
        ),
    ]

    objects = UserManager()

    email = models.EmailField(
        unique=True
    )

    nome_completo = models.CharField(
        max_length=255
    )

    telefone = models.CharField(
        max_length=30,
        blank=True
    )

    tipo_usuario = models.CharField(
        max_length=20,
        choices=USER_TYPE_CHOICES,
        default="cliente"
    )

    is_active = models.BooleanField(
        default=True
    )

    is_staff = models.BooleanField(
        default=False
    )

    date_joined = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    USERNAME_FIELD = "email"

    REQUIRED_FIELDS = [
        "nome_completo",
    ]

    class Meta:
        verbose_name = "Usuário"
        verbose_name_plural = "Usuários"
        ordering = [
            "-date_joined"
        ]

    def __str__(self):
        return self.email