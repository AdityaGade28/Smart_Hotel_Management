from django.contrib import admin
from .models import Hotel, Room


class RoomInline(admin.TabularInline):
    model = Room
    extra = 1
    fields = ['room_number', 'room_type', 'price_per_night', 'capacity', 'is_available']


@admin.register(Hotel)
class HotelAdmin(admin.ModelAdmin):
    inlines = [RoomInline]
    list_display = ['name', 'city', 'rating', 'is_active', 'get_available_rooms', 'created_at']
    list_filter = ['is_active', 'city', 'rating']
    search_fields = ['name', 'city', 'address']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ['room_number', 'hotel', 'room_type', 'price_per_night', 'capacity', 'is_available']
    list_filter = ['room_type', 'is_available', 'hotel']
    search_fields = ['room_number', 'hotel__name']
    list_editable = ['is_available']
