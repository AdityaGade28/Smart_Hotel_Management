from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class Hotel(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, default='India')
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    rating = models.DecimalField(
        max_digits=3, decimal_places=1,
        default=3.0,
        validators=[MinValueValidator(0), MaxValueValidator(5)]
    )
    image = models.ImageField(upload_to='hotel_images/', blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    amenities = models.TextField(blank=True, help_text='Comma-separated list of amenities')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-rating', 'name']

    def __str__(self):
        return self.name

    def get_available_rooms(self):
        return self.rooms.filter(is_available=True).count()

    def get_min_price(self):
        rooms = self.rooms.filter(is_available=True)
        if rooms.exists():
            return rooms.order_by('price_per_night').first().price_per_night
        return None

    def get_amenities_list(self):
        if self.amenities:
            return [a.strip() for a in self.amenities.split(',')]
        return []

    def recommendation_score(self):
        """
        score = (rating * 0.5) + (availability_score * 0.3) + (price_score * 0.2)
        """
        total_rooms = self.rooms.count()
        available_rooms = self.get_available_rooms()
        min_price = self.get_min_price()

        rating_score = float(self.rating) / 5.0

        # availability_score: normalized available rooms
        if total_rooms > 0:
            availability_score = available_rooms / total_rooms
        else:
            availability_score = 0

        # price_score: inverse of price (lower price = higher score), normalized 0-1
        if min_price and min_price > 0:
            # Assuming max price ~20000, min ~500
            MAX_PRICE = 20000
            price_score = max(0, 1 - (float(min_price) / MAX_PRICE))
        else:
            price_score = 0

        score = (rating_score * 0.5) + (availability_score * 0.3) + (price_score * 0.2)
        return round(score, 4)


class Room(models.Model):
    ROOM_TYPE_CHOICES = [
        ('single', 'Single'),
        ('double', 'Double'),
        ('deluxe', 'Deluxe'),
        ('suite', 'Suite'),
    ]

    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name='rooms')
    room_number = models.CharField(max_length=10)
    room_type = models.CharField(max_length=20, choices=ROOM_TYPE_CHOICES, default='single')
    price_per_night = models.DecimalField(max_digits=10, decimal_places=2)
    capacity = models.PositiveIntegerField(default=1)
    description = models.TextField(blank=True)
    amenities = models.TextField(blank=True, help_text='Comma-separated amenities')
    image = models.ImageField(upload_to='room_images/', blank=True, null=True)
    floor = models.PositiveIntegerField(default=1)
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['hotel', 'room_number']
        ordering = ['room_type', 'price_per_night']

    def __str__(self):
        return f"Room {self.room_number} - {self.hotel.name} ({self.get_room_type_display()})"

    def get_amenities_list(self):
        if self.amenities:
            return [a.strip() for a in self.amenities.split(',')]
        return []
