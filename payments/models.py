import uuid
from django.db import models
from bookings.models import Booking


class Payment(models.Model):
    METHOD_CHOICES = [
        ('card', 'Credit / Debit Card'),
        ('upi', 'UPI'),
        ('netbanking', 'Net Banking'),
        ('cash', 'Cash at Hotel'),
        ('wallet', 'Digital Wallet'),
    ]
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]

    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='payment')
    transaction_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    method = models.CharField(max_length=20, choices=METHOD_CHOICES, default='card')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Razorpay Specific Fields
    razorpay_order_id = models.CharField(max_length=100, blank=True, null=True)
    razorpay_payment_id = models.CharField(max_length=100, blank=True, null=True)
    razorpay_signature = models.CharField(max_length=100, blank=True, null=True)
    
    gateway_response = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Payment {str(self.transaction_id)[:8].upper()} — ₹{self.amount} [{self.status}]"

    @property
    def short_txn_id(self):
        return str(self.transaction_id)[:8].upper()
