"""
Real-time data API views — polled by frontend JavaScript every few seconds.
These endpoints return JSON used by AJAX auto-refresh on dashboards and pages.
"""
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Sum, Count


@login_required
def realtime_admin_stats(request):
    """Admin dashboard real-time KPI data — polled every 15 seconds."""
    if not request.user.is_admin_user():
        return JsonResponse({'error': 'Forbidden'}, status=403)

    from hotels.models import Hotel, Room
    from bookings.models import Booking
    from payments.models import Payment

    total_hotels = Hotel.objects.filter(is_active=True).count()
    total_rooms = Room.objects.count()
    available_rooms = Room.objects.filter(is_available=True).count()
    total_bookings = Booking.objects.count()
    confirmed = Booking.objects.filter(status='confirmed').count()
    pending = Booking.objects.filter(status='pending').count()
    cancelled = Booking.objects.filter(status='cancelled').count()
    revenue = Payment.objects.filter(status='completed').aggregate(
        total=Sum('amount')
    )['total'] or 0
    occupancy_rate = round(((total_rooms - available_rooms) / total_rooms) * 100, 1) if total_rooms > 0 else 0

    # Recent bookings (last 5)
    recent_bookings = []
    for b in Booking.objects.select_related('customer', 'room__hotel').order_by('-created_at')[:5]:
        recent_bookings.append({
            'id': b.pk,
            'booking_id': b.short_booking_id,
            'customer': b.customer.username,
            'hotel': b.room.hotel.name,
            'check_in': str(b.check_in),
            'status': b.status,
            'total': str(b.total_price),
        })

    return JsonResponse({
        'timestamp': timezone.now().strftime('%H:%M:%S'),
        'total_hotels': total_hotels,
        'total_rooms': total_rooms,
        'available_rooms': available_rooms,
        'total_bookings': total_bookings,
        'confirmed_bookings': confirmed,
        'pending_bookings': pending,
        'cancelled_bookings': cancelled,
        'total_revenue': float(revenue),
        'occupancy_rate': occupancy_rate,
        'recent_bookings': recent_bookings,
    })


@login_required
def realtime_customer_stats(request):
    """Customer dashboard real-time stats — polled every 20 seconds."""
    from bookings.models import Booking
    bookings = Booking.objects.filter(customer=request.user)
    total = bookings.count()
    active = bookings.filter(status='confirmed').count()
    pending = bookings.filter(status='pending').count()
    cancelled = bookings.filter(status='cancelled').count()

    recent = []
    for b in bookings.select_related('room__hotel').order_by('-created_at')[:5]:
        recent.append({
            'id': b.pk,
            'booking_id': b.short_booking_id,
            'hotel': b.room.hotel.name,
            'check_in': str(b.check_in),
            'check_out': str(b.check_out),
            'status': b.status,
            'total': str(b.total_price),
        })

    return JsonResponse({
        'timestamp': timezone.now().strftime('%H:%M:%S'),
        'total_bookings': total,
        'active_bookings': active,
        'pending_bookings': pending,
        'cancelled_bookings': cancelled,
        'recent_bookings': recent,
    })


def realtime_room_availability(request, room_pk):
    """Check live room availability — called from booking form."""
    from hotels.models import Room
    from bookings.models import Booking
    try:
        room = Room.objects.select_related('hotel').get(pk=room_pk)
    except Room.DoesNotExist:
        return JsonResponse({'available': False, 'message': 'Room not found'}, status=404)

    check_in = request.GET.get('check_in')
    check_out = request.GET.get('check_out')

    if check_in and check_out:
        from datetime import datetime
        try:
            ci = datetime.strptime(check_in, '%Y-%m-%d').date()
            co = datetime.strptime(check_out, '%Y-%m-%d').date()
            overlapping = Booking.objects.filter(
                room=room,
                status__in=['confirmed', 'pending'],
                check_in__lt=co,
                check_out__gt=ci
            ).exists()
            available = not overlapping and room.is_available
        except ValueError:
            available = room.is_available
    else:
        available = room.is_available

    return JsonResponse({
        'available': available,
        'room_id': room.pk,
        'room_number': room.room_number,
        'room_type': room.get_room_type_display(),
        'price_per_night': str(room.price_per_night),
        'hotel': room.hotel.name,
        'message': 'Available ✓' if available else 'Not available for selected dates',
        'timestamp': timezone.now().strftime('%H:%M:%S'),
    })


def realtime_hotel_stats(request, hotel_pk):
    """Live hotel stats for map popup refresh."""
    from hotels.models import Hotel
    try:
        hotel = Hotel.objects.get(pk=hotel_pk, is_active=True)
    except Hotel.DoesNotExist:
        return JsonResponse({'error': 'Not found'}, status=404)

    return JsonResponse({
        'hotel_id': hotel.pk,
        'available_rooms': hotel.get_available_rooms(),
        'min_price': str(hotel.get_min_price()) if hotel.get_min_price() else None,
        'rating': float(hotel.rating),
        'score': hotel.recommendation_score(),
        'timestamp': timezone.now().strftime('%H:%M:%S'),
    })


@login_required
def realtime_notifications(request):
    """Unread notification count for navbar badge — polled every 30 seconds."""
    from bookings.models import Booking
    pending_payments = Booking.objects.filter(
        customer=request.user,
        status='pending',
    ).exclude(payment__status='completed').count()

    # Admin: pending bookings needing attention
    if request.user.is_admin_user():
        pending_bookings = Booking.objects.filter(status='pending').count()
        from food_services.models import Order, ServiceRequest
        pending_orders = Order.objects.filter(status='pending').count()
        pending_services = ServiceRequest.objects.filter(status='pending').count()
        total_alerts = pending_bookings + pending_orders + pending_services
        return JsonResponse({
            'total_alerts': total_alerts,
            'pending_bookings': pending_bookings,
            'pending_orders': pending_orders,
            'pending_services': pending_services,
            'timestamp': timezone.now().strftime('%H:%M:%S'),
        })

    return JsonResponse({
        'total_alerts': pending_payments,
        'pending_payments': pending_payments,
        'timestamp': timezone.now().strftime('%H:%M:%S'),
    })
