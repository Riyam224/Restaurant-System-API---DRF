from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator
from decimal import Decimal


# Create your models here.
class Category(models.Model):
    name = models.CharField(
        max_length=100, unique=True, verbose_name=_("category name")
    )
    image = models.URLField(_("category image"), max_length=200, blank=True, null=True)
    is_active = models.BooleanField(default=True, verbose_name=_("is active"))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        verbose_name = _("Category")
        verbose_name_plural = _("Categories")

    def __str__(self):
        return self.name

# todo fix this 
class Product(models.Model):
    category = models.ForeignKey(
        Category,
        related_name="products",
        verbose_name=_("product category"),
        on_delete=models.CASCADE,
    )
    name = models.CharField(max_length=100, verbose_name=_("product name"))
    description = models.TextField(verbose_name=_("product description"), blank=True)
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name=_("price"),
        validators=[MinValueValidator(Decimal("0.01"))],
    )
    image = models.URLField(_("product image"), max_length=200, blank=True, null=True)
    is_available = models.BooleanField(default=True, verbose_name=_("is available"))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Product"
        verbose_name_plural = "Products"


class ProductInventory(models.Model):
    """
    Track product inventory/stock levels

    Business Rules:
    - Each product has one inventory record
    - Quantity decreases on order, increases on cancellation
    - Low stock alerts when quantity below threshold
    - Can mark products as out of stock automatically
    """

    product = models.OneToOneField(
        Product,
        on_delete=models.CASCADE,
        related_name="inventory",
        help_text="Product this inventory tracks"
    )

    quantity = models.PositiveIntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Current stock quantity"
    )

    low_stock_threshold = models.PositiveIntegerField(
        default=10,
        validators=[MinValueValidator(0)],
        help_text="Alert when stock falls below this level"
    )

    auto_disable_on_zero = models.BooleanField(
        default=True,
        help_text="Automatically mark product unavailable when stock is 0"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Product Inventory"
        verbose_name_plural = "Product Inventories"
        indexes = [
            models.Index(fields=["quantity"]),
        ]

    def __str__(self):
        return f"{self.product.name} - {self.quantity} in stock"

    def is_low_stock(self) -> bool:
        """Check if stock is below threshold"""
        return self.quantity <= self.low_stock_threshold

    def is_out_of_stock(self) -> bool:
        """Check if product is out of stock"""
        return self.quantity == 0

    def save(self, *args, **kwargs):
        """Auto-disable product if out of stock"""
        super().save(*args, **kwargs)

        if self.auto_disable_on_zero and self.is_out_of_stock():
            if self.product.is_available:
                self.product.is_available = False
                self.product.save(update_fields=['is_available'])


class InventoryTransaction(models.Model):
    """
    Track all inventory changes for audit trail

    Business Rules:
    - Record every stock change
    - Link to orders when relevant
    - Support manual adjustments
    """

    TRANSACTION_TYPE_CHOICES = (
        ('order', 'Order Placed'),
        ('cancellation', 'Order Cancelled'),
        ('restock', 'Manual Restock'),
        ('adjustment', 'Manual Adjustment'),
        ('damaged', 'Damaged/Expired'),
    )

    inventory = models.ForeignKey(
        ProductInventory,
        on_delete=models.CASCADE,
        related_name="transactions"
    )

    transaction_type = models.CharField(
        max_length=20,
        choices=TRANSACTION_TYPE_CHOICES
    )

    quantity_change = models.IntegerField(
        help_text="Positive for additions, negative for reductions"
    )

    quantity_after = models.PositiveIntegerField(
        help_text="Stock quantity after this transaction"
    )

    order_id = models.IntegerField(
        null=True,
        blank=True,
        help_text="Related order ID if applicable"
    )

    notes = models.TextField(
        blank=True,
        help_text="Additional notes about this transaction"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["inventory", "-created_at"]),
            models.Index(fields=["transaction_type"]),
        ]

    def __str__(self):
        return f"{self.get_transaction_type_display()}: {self.quantity_change:+d} for {self.inventory.product.name}"
