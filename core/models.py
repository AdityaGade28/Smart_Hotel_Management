from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User

# Room model (optional, for future extension)
class Room(models.Model):
    ROOM_TYPES = [
        ('Single', 'Single'),
        ('Double', 'Double'),
        ('Deluxe', 'Deluxe'),
        ('Suite', 'Suite'),
        ('Family', 'Family'),
        ('Business', 'Business'),
    ]
    BEDDING_TYPES = [
        ('Single Bed', 'Single Bed'),
        ('Double Bed', 'Double Bed'),
    ]

    room_type = models.CharField(max_length=50, choices=ROOM_TYPES)
    bedding_type = models.CharField(max_length=50, choices=BEDDING_TYPES)
    price_per_night = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.room_type} ({self.bedding_type})"

# Booking model
class Booking(models.Model):
    MEAL_PLANS = [
        ('Breakfast', 'Breakfast'),
        ('All Meals', 'All Meals'),
        ('None', 'None'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    email = models.EmailField()
    mobile = models.CharField(max_length=15)
    country = models.CharField(max_length=50)

    room_type = models.CharField(max_length=50)
    bedding_type = models.CharField(max_length=50)
    num_rooms = models.PositiveIntegerField()
    meal_plan = models.CharField(max_length=20, choices=MEAL_PLANS)
    check_in = models.DateField()
    check_out = models.DateField()
    booking_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default='Pending')  # Pending, Confirmed, Cancelled

    def __str__(self):
        return f"{self.name} - {self.room_type} ({self.status})"

# Payment model
class Payment(models.Model):
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE)
    total_amount = models.PositiveIntegerField()
    payment_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default='Pending')  # Pending, Paid, Failed

    def __str__(self):
        return f"Payment - {self.booking.name} ({self.status})"

# Optional: Staff model (extra info)
class Staff(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=50)  # Manager, Receptionist, Cleaner, Chef

    def __str__(self):
        return f"{self.user.username} - {self.role}"
