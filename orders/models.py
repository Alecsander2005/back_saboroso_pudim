from django.db import models


class Order(models.Model):
    STATUS_CHOICES = [
        ("pendente", "Pendente"),
        ("preparando", "Preparando"),
        ("pronto", "Pronto"),
        ("entregue", "Entregue"),
        ("cancelado", "Cancelado"),
    ]

    DELIVERY_METHOD_CHOICES = [
        ("entrega", "Entrega"),
        ("retirada", "Retirada"),
    ]

    customer_name = models.CharField(
        max_length=255
    )

    customer_email = models.EmailField(
        blank=True
    )

    customer_whatsapp = models.CharField(
        max_length=30
    )

    delivery_date = models.DateField(
        null=True,
        blank=True
    )

    delivery_method = models.CharField(
        max_length=20,
        choices=DELIVERY_METHOD_CHOICES
    )

    address = models.TextField(
        blank=True
    )

    address_rua = models.CharField(
        max_length=255,
        blank=True
    )

    address_bairro = models.CharField(
        max_length=255,
        blank=True
    )

    address_numero = models.CharField(
        max_length=30,
        blank=True
    )

    address_complemento = models.CharField(
        max_length=255,
        blank=True
    )

    address_referencia = models.CharField(
        max_length=255,
        blank=True
    )

    total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    delivery_fee = models.DecimalField(
        max_digits= 10,
        decimal_places= 2,
        default = 0 
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pendente"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Pedido"
        verbose_name_plural = "Pedidos"

    def __str__(self):
        return f"Pedido #{self.id} - {self.customer_name}"


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items"
    )

    product = models.ForeignKey(
        "products.Product",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="order_items"
    )

    product_name = models.CharField(
        max_length=255
    )

    size = models.CharField(
        max_length=100
    )

    quantity = models.PositiveIntegerField(
        default=1
    )

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        verbose_name = "Item do pedido"
        verbose_name_plural = "Itens do pedido"

    @property
    def subtotal(self):
        return self.price * self.quantity

    def __str__(self):
        return f"{self.product_name} - {self.size}"