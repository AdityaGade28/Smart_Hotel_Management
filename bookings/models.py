import uuid
from django.db import models
from users.models import CustomUser
from hotels.models import Room


class Booking(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    ]

    booking_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    customer = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='bookings')
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='bookings')
    check_in = models.DateField()
    check_out = models.DateField()
    num_guests = models.PositiveIntegerField(default=1)
    special_requests = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    total_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    coupon_code = models.CharField(max_length=50, blank=True)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Booking {str(self.booking_id)[:8].upper()} — {self.customer.username}"

    def get_num_nights(self):
        delta = self.check_out - self.check_in
        return max(delta.days, 1)

    def calculate_total(self):
        nights = self.get_num_nights()
        subtotal = self.room.price_per_night * nights
        return max(subtotal - self.discount_amount, 0)

    def save(self, *args, **kwargs):
        self.total_price = self.calculate_total()
        super().save(*args, **kwargs)

    @property
    def short_booking_id(self):
        return str(self.booking_id)[:8].upper()


class Coupon(models.Model):
    code = models.CharField(max_length=50, unique=True)
    discount_type = models.CharField(max_length=10, choices=[('flat', 'Flat'), ('percent', 'Percent')], default='flat')
    discount_value = models.DecimalField(max_digits=10, decimal_places=2)
    max_uses = models.PositiveIntegerField(default=100)
    used_count = models.PositiveIntegerField(default=0)
    valid_from = models.DateField()
    valid_until = models.DateField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"Coupon {self.code} ({self.discount_type}: {self.discount_value})"

    def is_valid(self):
        from django.utils import timezone
        today = timezone.now().date()
        return self.is_active and self.valid_from <= today <= self.valid_until and self.used_count < self.max_uses

    def apply(self, price):
        if not self.is_valid():
            return 0
        if self.discount_type == 'percent':
            return round(price * self.discount_value / 100, 2)
        return min(self.discount_value, price)
