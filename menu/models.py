from django.db import models
from django.utils.translation import gettext_lazy as _


# Create your models here.
class Category(models.Model):
    name = models.CharField(
        max_length=100, unique=True, verbose_name=_("category name")
    )
    image = models.URLField(_("category image"), max_length=200, blank=True, null=True)
    is_active = models.BooleanField(default=True, verbose_name=_("is active"))
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]
        verbose_name = _("Category")
        verbose_name_plural = _("Categories")

    def __str__(self):
        return self.name


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
        max_digits=10, decimal_places=2, verbose_name=_("price")
    )
    image = models.URLField(_("product image"), max_length=200, blank=True, null=True)
    is_available = models.BooleanField(default=True, verbose_name=_("is available"))
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Product"
        verbose_name_plural = "Products"
