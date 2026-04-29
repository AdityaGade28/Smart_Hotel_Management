from django.contrib import admin
from .models import Booking, Coupon


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['short_booking_id', 'customer', 'room', 'check_in', 'check_out', 'status', 'total_price', 'created_at']
    list_filter = ['status', 'check_in', 'check_out']
    search_fields = ['customer__username', 'room__hotel__name', 'booking_id']
    readonly_fields = ['booking_id', 'created_at', 'updated_at']
    list_editable = ['status']


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ['code', 'discount_type', 'discount_value', 'used_count', 'max_uses', 'valid_until', 'is_active']
    list_filter = ['is_active', 'discount_type']
    search_fields = ['code']
