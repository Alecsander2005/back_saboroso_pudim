from django.db import models

class Order(models.Model):
    STATUS_CHOICES =[
        ("Pending", "Pendente"),
        ("Confirmed", "confirmado"),
        ("Preparing", "preparando"),
        ("Ready", "pronto"),
        ("delivered", "entregue"),
        ("cancelled", "cancelado"),
    ]

    DELIVERY_CHOICES=[
        ("delivery", "entrega"),
        ("pickup", "retirada"),
    ]

    customer_name = models.CharField(max_length=255)
    customer_email= models.EmailField(blank=True)
    customer_whatsapp = models.CharField(max_length=30)

    delivery_method = models.CharField(
        max_length = 20, 
        choices = DELIVERY_CHOICES
    )

    delivey_date = models.DateField()

    address = models.TextField(blank = True)

    status = models.CharField(
        max_length=20,
        choices= STATUS_CHOICES,
        default= "pending"
    )

    total = models.DecimalField(
        max_digits = 10,
        decimal_places= 2,
        default = 0
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "pedido"
        verbose_name_plural = "pedidos"

    def __str__(self):
        return f"Pedido {self.id} - {self.customer_name} - {self.status}"

class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete= models.CASCADE,
        related_name= "items"
    )

    product = models.ForeignKey(
        "products.Product",
        on_delete= models.SET_NULL,
        null= True,
        blank = True,
        related_name="order_items"
    )

    product_name = models.CharField(max_length=255)

    size_name = models.CharField(max_length=100)

    quantity = models.PositiveIntegerField()

    unit_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )

    subtotal = models.DecimalField(
        max_digits = 10,
        decimal_places = 2,
    )
