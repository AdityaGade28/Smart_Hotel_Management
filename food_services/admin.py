from django.contrib import admin
from .models import MenuItem, Order, OrderItem, ServiceRequest


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['subtotal']


@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price', 'is_veg', 'is_available']
    list_filter = ['category', 'is_veg', 'is_available']
    search_fields = ['name']
    list_editable = ['is_available', 'price']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    inlines = [OrderItemInline]
    list_display = ['pk', 'booking', 'status', 'total', 'created_at']
    list_filter = ['status']
    list_editable = ['status']


@admin.register(ServiceRequest)
class ServiceRequestAdmin(admin.ModelAdmin):
    list_display = ['pk', 'booking', 'service_type', 'status', 'requested_at']
    list_filter = ['service_type', 'status']
    list_editable = ['status']
