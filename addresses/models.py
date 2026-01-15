from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="addresses")
    label = models.CharField(max_length=50)
    city = models.CharField(max_length=100)
    street = models.CharField(max_length=255)
    building = models.CharField(max_length=50, blank=True)
    lat = models.DecimalField(max_digits=9, decimal_places=6)
    lng = models.DecimalField(max_digits=9, decimal_places=6)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.label}: {self.street}, {self.city}"
