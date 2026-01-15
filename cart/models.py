from django.db import models
from django.utils import timezone

# Create your models here.
from django.contrib.auth.models import User

from menu.models import Product


class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="cart")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def total_items(self):
        return sum(item.quantity for item in self.items.all())

    def total_price(self):
        return sum(item.subtotal() for item in self.items.all())

    def __str__(self):
        return f"Cart ({self.user.username})"

    class Meta:

        verbose_name = "Cart"
        verbose_name_plural = "Carts"


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name="items", on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"

    def subtotal(self):
        return self.product.price * self.quantity
