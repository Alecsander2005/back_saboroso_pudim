from django.db import models


class StoreSettings(models.Model):
    store_name = models.CharField(
        max_length=255,
        default= "Saboroso Pudim"
        )

    description = models.TextField(
        blank = True
    )

    whatsapp = models.CharField(
        max_length=30,
        blank=True
    )

    email = models.EmailField(
        blank=True
    )

    address = models.TextField(
        blank = True
    )

    logo = models.ImageField(
        upload_to= "store/",
        blank= True,
        null = True,

    )

    is_open = models.BooleanField(
        default = True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now = True
    )

    class Meta:
        verbose_name = "Configuração da loja"
        verbose_name_plural = "Configurações da loja"

    def __str__(self):
        return self.store_name

    def save(self,*args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)