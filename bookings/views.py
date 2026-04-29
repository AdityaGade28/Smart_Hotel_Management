from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from hotels.models import Hotel, Room
from .models import Booking, Coupon
from .forms import BookingForm


@login_required
def hotel_rooms(request, hotel_pk):
    """Show rooms for a specific hotel to book from."""
    hotel = get_object_or_404(Hotel, pk=hotel_pk, is_active=True)
    check_in = request.GET.get('check_in')
    check_out = request.GET.get('check_out')
    rooms = hotel.rooms.filter(is_available=True)
    context = {
        'hotel': hotel,
        'rooms': rooms,
        'check_in': check_in,
        'check_out': check_out,
    }
    return render(request, 'bookings/hotel_rooms.html', context)


@login_required
def book_room(request, room_pk):
    room = get_object_or_404(Room, pk=room_pk)
    hotel = room.hotel

    if not room.is_available:
        messages.error(request, 'This room is currently not available.')
        return redirect('hotels:hotel_detail', pk=hotel.pk)

    discount_amount = 0
    coupon_obj = None

    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            check_in = form.cleaned_data['check_in']
            check_out = form.cleaned_data['check_out']
            coupon_code = form.cleaned_data.get('coupon_code', '')

            # Check overlapping bookings
            overlapping = Booking.objects.filter(
                room=room,
                status__in=['confirmed', 'pending'],
                check_in__lt=check_out,
                check_out__gt=check_in
            ).exists()

            if overlapping:
                messages.error(request, 'Room is not available for the selected dates.')
                return render(request, 'bookings/book_room.html', {
                    'form': form, 'room': room, 'hotel': hotel
                })

            # Apply coupon
            if coupon_code:
                try:
                    coupon_obj = Coupon.objects.get(code__iexact=coupon_code, is_active=True)
                    if coupon_obj.is_valid():
                        nights = (check_out - check_in).days
                        subtotal = room.price_per_night * nights
                        discount_amount = coupon_obj.apply(subtotal)
                        coupon_obj.used_count += 1
                        coupon_obj.save()
                    else:
                        messages.warning(request, 'Coupon is expired or invalid.')
                        coupon_code = ''
                except Coupon.DoesNotExist:
                    messages.warning(request, 'Coupon code not found.')
                    coupon_code = ''

            booking = form.save(commit=False)
            booking.customer = request.user
            booking.room = room
            booking.discount_amount = discount_amount
            booking.coupon_code = coupon_code if coupon_obj else ''
            booking.status = 'pending'
            booking.save()

            # Send confirmation email
            try:
                send_mail(
                    subject=f'Booking Confirmation - {booking.short_booking_id}',
                    message=f'''Dear {request.user.username},

Your booking has been created successfully!

Booking ID: {booking.short_booking_id}
Hotel: {hotel.name}
Room: {room.room_number} ({room.get_room_type_display()})
Check-in: {check_in}
Check-out: {check_out}
Total: ₹{booking.total_price}
Status: Pending

Please complete payment to confirm your booking.

Thank you for choosing us!
''',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[request.user.email],
                    fail_silently=True,
                )
            except Exception:
                pass

            messages.success(request, f'Booking {booking.short_booking_id} created! Please complete payment.')
            return redirect('payments:checkout', booking_pk=booking.pk)
    else:
        initial = {}
        check_in = request.GET.get('check_in')
        check_out = request.GET.get('check_out')
        if check_in:
            initial['check_in'] = check_in
        if check_out:
            initial['check_out'] = check_out
        form = BookingForm(initial=initial)

    context = {
        'form': form,
        'room': room,
        'hotel': hotel,
    }
    return render(request, 'bookings/book_room.html', context)


@login_required
def booking_list(request):
    if request.user.is_admin_user():
        bookings = Booking.objects.select_related('customer', 'room__hotel').all()
    else:
        bookings = Booking.objects.filter(customer=request.user).select_related('room__hotel')
    
    status_filter = request.GET.get('status', '')
    if status_filter:
        bookings = bookings.filter(status=status_filter)

    return render(request, 'bookings/booking_list.html', {
        'bookings': bookings,
        'status_filter': status_filter,
    })


@login_required
def booking_detail(request, pk):
    if request.user.is_admin_user():
        booking = get_object_or_404(Booking, pk=pk)
    else:
        booking = get_object_or_404(Booking, pk=pk, customer=request.user)
    return render(request, 'bookings/booking_detail.html', {'booking': booking})


@login_required
def cancel_booking(request, pk):
    if request.user.is_admin_user():
        booking = get_object_or_404(Booking, pk=pk)
    else:
        booking = get_object_or_404(Booking, pk=pk, customer=request.user)

    if booking.status in ['confirmed', 'pending']:
        if request.method == 'POST':
            booking.status = 'cancelled'
            booking.save()
            # Free up the room
            booking.room.is_available = True
            booking.room.save()
            messages.success(request, f'Booking {booking.short_booking_id} cancelled successfully.')
            return redirect('bookings:booking_list')
        return render(request, 'bookings/cancel_confirm.html', {'booking': booking})
    else:
        messages.error(request, 'This booking cannot be cancelled.')
        return redirect('bookings:booking_detail', pk=pk)


@login_required
def admin_update_status(request, pk):
    if not request.user.is_admin_user():
        messages.error(request, 'Access denied.')
        return redirect('hotels:home')
    booking = get_object_or_404(Booking, pk=pk)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in ['pending', 'confirmed', 'cancelled', 'completed']:
            old_status = booking.status
            booking.status = new_status
            booking.save()
            if new_status == 'confirmed':
                booking.room.is_available = False
                booking.room.save()
            elif new_status in ['cancelled', 'completed']:
                booking.room.is_available = True
                booking.room.save()
            messages.success(request, f'Booking status updated from {old_status} to {new_status}.')
    return redirect('bookings:booking_detail', pk=pk)


@login_required
def check_availability(request):
    """AJAX endpoint for date availability."""
    room_id = request.GET.get('room_id')
    check_in = request.GET.get('check_in')
    check_out = request.GET.get('check_out')
    from django.http import JsonResponse
    from datetime import datetime

    if not all([room_id, check_in, check_out]):
        return JsonResponse({'available': False, 'message': 'Missing parameters'})

    try:
        room = Room.objects.get(pk=room_id)
        check_in_dt = datetime.strptime(check_in, '%Y-%m-%d').date()
        check_out_dt = datetime.strptime(check_out, '%Y-%m-%d').date()

        overlapping = Booking.objects.filter(
            room=room,
            status__in=['confirmed', 'pending'],
            check_in__lt=check_out_dt,
            check_out__gt=check_in_dt
        ).exists()

        if overlapping:
            return JsonResponse({'available': False, 'message': 'Room not available for selected dates'})
        return JsonResponse({'available': True, 'message': 'Room is available!'})
    except Exception as e:
        return JsonResponse({'available': False, 'message': str(e)})
