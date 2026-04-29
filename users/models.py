from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Admin / Hotel Manager'),
        ('customer', 'Customer / Guest'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='customer')
    phone = models.CharField(max_length=15, blank=True)

    def is_admin_user(self):
        return self.role == 'admin' or self.is_staff or self.is_superuser

    def is_customer(self):
        return self.role == 'customer'

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"


class Profile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='profile')
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    photo = models.ImageField(upload_to='profile_photos/', blank=True, null=True)
    date_of_birth = models.DateField(null=True, blank=True)
    bio = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Profile of {self.user.username}"
