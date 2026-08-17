from django.db import models

class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    image = models.ImageField(
        upload_to = "products/",
        blank = True,
        null = True
    )
    is_active = models.BooleanField(default=True)

    create_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now = True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Produto"
        verbose_name_plural = "Produtos"

    def __str__(self):
        return self.name


class ProductSize(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="sizes"
    )

    label = models.CharField(max_length=100)


    price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["price"]
        verbose_name = "Tamanho"
        verbose_name_plural = "Tamanhos"

    def __str__(self):
        return f"{self.product.name} - {self.name}"

