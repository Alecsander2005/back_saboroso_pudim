from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from .crypto import email_lookup, normalize_email
from .fields import EncryptedEmailField
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

    email = EncryptedEmailField(max_length=512, unique=True)

    email_lookup = models.CharField(
        max_length=64,
        unique=True,
        editable=False,
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

    def save(self, *args, **kwargs):
        self.email = normalize_email(self.email)
        self.email_lookup = email_lookup(self.email)

        update_fields = kwargs.get("update_fields")
        if update_fields is not None and "email" in update_fields:
            kwargs["update_fields"] = set(update_fields) | {"email_lookup"}

        super().save(*args, **kwargs)