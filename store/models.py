from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models


class StoreSettings(models.Model):

    name = models.CharField(
        max_length=255,
        default="Saboroso Pudim"
    )

    phone = models.CharField(
        max_length=30,
        blank=True
    )

    whatsapp = models.CharField(
        max_length=30,
        blank=True
    )

    address = models.TextField(
        blank=True
    )

    taxa_entrega = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[
            MinValueValidator(0)
        ]
    )

    pedido_minimo = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[
            MinValueValidator(0)
        ]
    )

    loja_aberta = models.BooleanField(
        default=True
    )

    horario_abertura = models.TimeField(
        null=True,
        blank=True
    )

    horario_fechamento = models.TimeField(
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        verbose_name = "Configuração da loja"
        verbose_name_plural = "Configurações da loja"

    def __str__(self):
        return self.name