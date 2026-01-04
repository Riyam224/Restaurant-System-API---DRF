# Create your models here.
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Order(models.Model):

    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("preparing", "Preparing"),
        ("on_the_way", "On the way"),
        ("delivered", "Delivered"),
        ("cancelled", "Cancelled"),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="orders")

    total_price = models.DecimalField(max_digits=10, decimal_places=2)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Order #{self.id} - {self.user}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name="items", on_delete=models.CASCADE)

    product_id = models.IntegerField()
    product_name = models.CharField(max_length=255)

    price = models.DecimalField(max_digits=10, decimal_places=2)

    quantity = models.PositiveIntegerField()

    def subtotal(self):
        return self.price * self.quantity

    def __str__(self):
        return f"{self.product_name} x {self.quantity}"
