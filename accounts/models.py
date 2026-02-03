from django.db import models
from django.conf import settings
from django.utils import timezone
import random
import string
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    ROLE_CHOICES = (
        ("customer", "Customer"),
        ("admin", "Admin"),
        ("restaurant", "Restaurant"),
    )
    phone = models.CharField(max_length=15, blank=True, null=True)
    avatar = models.URLField(blank=True, null=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="customer")
    is_verified = models.BooleanField(default=False)


class PasswordResetOTP(models.Model):
    """Model to store OTP for password reset"""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)
    expires_at = models.DateTimeField()

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"OTP for {self.user.email} - {self.otp}"

    @staticmethod
    def generate_otp():
        """Generate a 6-digit OTP"""
        return "".join(random.choices(string.digits, k=6))

    def is_valid(self):
        """Check if OTP is still valid"""
        return not self.is_used and timezone.now() < self.expires_at

    @classmethod
    def create_otp(cls, user):
        """Create a new OTP for user"""
        otp = cls.generate_otp()
        expires_at = timezone.now() + timezone.timedelta(
            minutes=10
        )  # OTP valid for 10 minutes
        return cls.objects.create(user=user, otp=otp, expires_at=expires_at)
