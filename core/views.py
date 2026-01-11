from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from .models import Booking, Payment, Staff
from datetime import datetime

# -----------------------------------------
# Public Pages
# -----------------------------------------
def home(request):
    return render(request, 'home.html')

def facilities(request):
    return render(request, 'facilities.html')

def contact(request):
    return render(request, 'contact.html')


# -----------------------------------------
# User Booking
# -----------------------------------------
@login_required
def book_room(request):
    if request.method == 'POST':
        # Get form data
        name = request.POST.get('name')
        email = request.POST.get('email')
        mobile = request.POST.get('mobile')
        country = request.POST.get('country')
        room_type = request.POST.get('room_type')
        bedding_type = request.POST.get('bedding_type')
        num_rooms = int(request.POST.get('num_rooms'))
        meal_plan = request.POST.get('meal_plan')
        check_in = request.POST.get('check_in')
        check_out = request.POST.get('check_out')

        # Create Booking
        booking = Booking.objects.create(
            user=request.user,
            name=name,
            email=email,
            mobile=mobile,
            country=country,
            room_type=room_type,
            bedding_type=bedding_type,
            num_rooms=num_rooms,
            meal_plan=meal_plan,
            check_in=check_in,
            check_out=check_out,
            status='Pending'
        )

        # Calculate total amount
        room_prices = {'Single':1000, 'Double':1500, 'Deluxe':2500, 'Suite':4000, 'Family':3000, 'Business':2000}
        d1 = datetime.strptime(check_in, '%Y-%m-%d')
        d2 = datetime.strptime(check_out, '%Y-%m-%d')
        nights = (d2 - d1).days
        total_amount = room_prices.get(room_type, 1000) * num_rooms * nights

        # Create Payment
        Payment.objects.create(
            booking=booking,
            total_amount=total_amount,
            status='Pending'
        )

        return redirect('home')  # Redirect after booking

    return render(request, 'book_room.html')


# -----------------------------------------
# Admin Access Check
# -----------------------------------------
def admin_required(user):
    return user.is_staff


# -----------------------------------------
# Admin Dashboard
# -----------------------------------------
@login_required
@user_passes_test(admin_required)
def dashboard(request):
    total_bookings = Booking.objects.count()
    total_payments = Payment.objects.count()
    total_staff = Staff.objects.count()
    context = {
        'total_bookings': total_bookings,
        'total_payments': total_payments,
        'total_staff': total_staff
    }
    return render(request, 'dashboard.html', context)


@login_required
@user_passes_test(lambda u: u.is_staff)
def dashboard(request):
    return render(request, 'dashboard.html')


# -----------------------------------------
# Bookings Page (Admin)
# -----------------------------------------
@login_required
@user_passes_test(admin_required)
def bookings(request):
    all_bookings = Booking.objects.all().order_by('-booking_date')

    # Handle confirm or delete actions
    if request.method == 'POST':
        booking_id = request.POST.get('booking_id')
        action = request.POST.get('action')
        booking = get_object_or_404(Booking, id=booking_id)

        if action == 'confirm':
            booking.status = 'Confirmed'
            booking.save()
        elif action == 'delete':
            booking.delete()

        return redirect('bookings')

    return render(request, 'bookings.html', {'bookings': all_bookings})


# -----------------------------------------
# Payments Page (Admin)
# -----------------------------------------
@login_required
@user_passes_test(admin_required)
def payments(request):
    all_payments = Payment.objects.select_related('booking').all().order_by('-payment_date')

    # Handle delete payment
    if request.method == 'POST':
        payment_id = request.POST.get('payment_id')
        action = request.POST.get('action')
        payment = get_object_or_404(Payment, id=payment_id)

        if action == 'delete':
            payment.delete()

        return redirect('payments')

    return render(request, 'payments.html', {'payments': all_payments})


# -----------------------------------------
# Staff Page (Admin)
# -----------------------------------------
@login_required
@user_passes_test(admin_required)
def staff(request):
    staff_list = Staff.objects.select_related('user').all()
    return render(request, 'staff.html', {'staff_list': staff_list})


# -----------------------------------------
# Invoice Page
# -----------------------------------------
@login_required
@user_passes_test(admin_required)
def invoice(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    payment = get_object_or_404(Payment, booking=booking)
    return render(request, 'invoice.html', {'booking': booking, 'payment': payment})

from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect

def custom_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            if user.is_staff:
                return redirect('/dashboard/')
            else:
                return redirect('/')
        else:
            return render(request, 'login.html', {'error': 'Invalid login'})
    return render(request, 'login.html')
