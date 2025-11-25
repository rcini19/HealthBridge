from uuid import uuid4
from datetime import date, timedelta

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class CustomUser(AbstractUser):
    class UserType(models.TextChoices):
        DONOR = 'donor', 'Donor'
        RECIPIENT = 'recipient', 'Recipient'
    
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    address = models.TextField(blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    
    # User role system - one-time selection, permanent
    user_type = models.CharField(
        max_length=10,
        choices=UserType.choices,
        blank=True,
        null=True,
        help_text="User role: Donor or Recipient (permanent after selection)"
    )
    role_selected = models.BooleanField(
        default=False,
        help_text="Has the user completed their one-time role selection?"
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.get_user_type_display() if self.user_type else 'No Role'})"
    
    @property
    def is_donor(self):
        return self.user_type == self.UserType.DONOR
    
    @property
    def is_recipient(self):
        return self.user_type == self.UserType.RECIPIENT


class GenericMedicine(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class BrandMedicine(models.Model):
    brand_name = models.CharField(max_length=100)
    generic = models.ForeignKey(GenericMedicine, on_delete=models.CASCADE, related_name='brands')

    def __str__(self):
        return f"{self.brand_name} ({self.generic.name})"


# ============================================================================
# NOTE: Models have been moved to their respective modular apps.
# This avoids model conflicts and follows Django best practices.
# 
# Active models are now in:
# - donations/models.py (Donation, ExpiryAlert)
# - requests/models.py (MedicineRequest)
# - notifications/models.py (Notification)
# - administrator app uses views only, no models
# ============================================================================
