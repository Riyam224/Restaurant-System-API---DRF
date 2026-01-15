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

    # Pricing
    subtotal = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        editable=False,
        help_text="Order subtotal before discount"
    )
    discount_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        editable=False,
        help_text="Discount applied from coupon"
    )
    total_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        editable=False,
        help_text="Final price after discount"
    )

    # Coupon
    coupon_code = models.CharField(
        max_length=50,
        blank=True,
        help_text="Coupon code used (if any)"
    )

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    payment_status = models.CharField(
        max_length=20,
        choices=[
            ("pending", "Pending"),
            ("paid", "Paid"),
            ("failed", "Failed"),
        ],
        default="pending",
    )
    address = models.ForeignKey("addresses.Address", on_delete=models.PROTECT)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        update_fields = kwargs.get("update_fields")
        is_create = self.pk is None
        old_status = None
        if not is_create and (update_fields is None or "status" in update_fields):
            old_status = (
                Order.objects.filter(pk=self.pk)
                .values_list("status", flat=True)
                .first()
            )
        super().save(*args, **kwargs)
        if is_create or (old_status is not None and old_status != self.status):
            OrderStatusHistory.objects.create(order=self, status=self.status)

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

    def update_order_total(self):
        total = sum(item.price * item.quantity for item in self.order.items.all())
        if self.order.total_price != total:
            self.order.total_price = total
            self.order.save(update_fields=["total_price"])

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.update_order_total()

    def delete(self, *args, **kwargs):
        order = self.order
        super().delete(*args, **kwargs)
        total = sum(item.price * item.quantity for item in order.items.all())
        if order.total_price != total:
            order.total_price = total
            order.save(update_fields=["total_price"])

    def __str__(self):
        return f"{self.product_name} x {self.quantity}"


class OrderStatusHistory(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="history")
    status = models.CharField(max_length=20, choices=Order.STATUS_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
