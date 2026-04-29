from django.contrib import admin
from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['short_txn_id', 'booking', 'amount', 'method', 'status', 'created_at']
    list_filter = ['status', 'method']
    search_fields = ['transaction_id', 'booking__customer__username']
    readonly_fields = ['transaction_id', 'created_at', 'updated_at']
