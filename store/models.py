from django.db import models


class StoreSettings(models.Model):
    loja_nome = models.CharField(
        max_length=255,
        default="Saboroso Pudim"
    )

    email = models.EmailField(
        blank=True
    )

    telefone = models.CharField(
        max_length=30,
        blank=True
    )

    endereco = models.TextField(
        blank=True
    )

    taxa_entrega = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    tempo_entrega = models.PositiveIntegerField(
        default=60,
        help_text="Tempo estimado de entrega em minutos."
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        verbose_name = "Configuração da loja"
        verbose_name_plural = "Configurações da loja"

    def __str__(self):
        return self.loja_nome