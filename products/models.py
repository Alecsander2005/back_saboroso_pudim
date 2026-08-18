from django.db import models
from django.core.validators import MinValueValidator


class Product(models.Model):

    name = models.CharField(
        max_length=255
    )

    description = models.TextField(
        blank=True
    )

    image = models.ImageField(
        upload_to="products/",
        blank=True,
        null=True
    )

    is_active = models.BooleanField(
        default=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class ProductSize(models.Model):

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="sizes"
    )

    label = models.CharField(
        max_length=100
    )

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )

    is_active = models.BooleanField(
        default=True
    )

    class Meta:
        ordering = ["price"]

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "product",
                    "label"
                ],
                name="unique_product_size"
            )
        ]

    def __str__(self):
        return (
            f"{self.product.name} - "
            f"{self.label}"
        )