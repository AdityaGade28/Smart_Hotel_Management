from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from .models import Booking, Payment, Staff
from datetime import datetime

def admin_required(user):
    return user.is_staff or user.is_superuser

# ---------------- Public Pages ----------------
def home(request):
    return render(request, 'home.html')

def facilities(request):
    return render(request, 'facilities.html')

def contact(request):
    return render(request, 'contact.html')

def map_view(request):
    return render(request, 'map.html')

# ---------------- User Booking ----------------
@login_required
def book_room(request):
    if request.method == 'POST':
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

        room_prices = {'Single':1000,'Double':1500,'Deluxe':2500,'Suite':4000}
        d1 = datetime.strptime(check_in, '%Y-%m-%d')
        d2 = datetime.strptime(check_out, '%Y-%m-%d')
        nights = (d2 - d1).days
        total_amount = room_prices.get(room_type,1000) * num_rooms * nights

        Payment.objects.create(
            booking=booking,
            total_amount=total_amount,
            status='Pending'
        )

        return redirect('profile')

    return render(request, 'book_room.html')

# ---------------- User Profile ----------------
@login_required
def user_profile(request):
    bookings = Booking.objects.filter(user=request.user).order_by('-booking_date')
    return render(request, 'profile.html', {'bookings': bookings})

# ---------------- Dashboard ----------------
@login_required
@user_passes_test(admin_required)
def dashboard(request):
    return render(request, 'dashboard.html', {
        'total_bookings': Booking.objects.count(),
        'total_payments': Payment.objects.count(),
        'total_staff': Staff.objects.count()
    })

# ---------------- Admin Pages ----------------
@login_required
@user_passes_test(admin_required)
def bookings(request):
    all_bookings = Booking.objects.all().order_by('-booking_date')

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

@login_required
@user_passes_test(admin_required)
def payments(request):
    all_payments = Payment.objects.select_related('booking').all().order_by('-payment_date')

    if request.method == 'POST':
        payment_id = request.POST.get('payment_id')
        payment = get_object_or_404(Payment, id=payment_id)
        payment.delete()
        return redirect('payments')

    return render(request, 'payments.html', {'payments': all_payments})

@login_required
@user_passes_test(admin_required)
def staff(request):
    staff_list = Staff.objects.select_related('user').all()
    return render(request, 'staff.html', {'staff_list': staff_list})

@login_required
@user_passes_test(admin_required)
def invoice(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    payment = get_object_or_404(Payment, booking=booking)
    return render(request, 'invoice.html', {'booking': booking, 'payment': payment})

# ---------------- Login ----------------
def custom_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            if user.is_staff or user.is_superuser:
                return redirect('dashboard')
            else:
                return redirect('profile')
        else:
            return render(request, 'login.html', {'error':'Invalid credentials'})

    return render(request, 'login.html')


from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Booking, Payment, Staff

def admin_required(user):
    return user.is_staff or user.is_superuser

@login_required
@user_passes_test(admin_required)
def dashboard(request):
    return render(request, 'dashboard.html', {
        'bookings': Booking.objects.count(),
        'payments': Payment.objects.count(),
        'staff': Staff.objects.count()
    })
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from .models import Booking, Payment

def custom_login(request):
    if request.method=='POST':
        username=request.POST['username']
        password=request.POST['password']
        user=authenticate(request,username=username,password=password)
        if user:
            login(request,user)
            return redirect('profile')
        else:
            return render(request,'login.html',{'error':'Invalid credentials'})
    return render(request,'login.html')

def register(request):
    if request.method=='POST':
        User.objects.create_user(
            username=request.POST['username'],
            email=request.POST['email'],
            password=request.POST['password']
        )
        return redirect('login')
    return redirect('login')

@login_required
def profile(request):
    bookings = Booking.objects.filter(user=request.user).order_by('-booking_date')
    return render(request,'profile.html',{'bookings':bookings})


from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect

def custom_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('profile')   # after login → profile
        else:
            return render(request, 'login.html', {'error':'Invalid username or password'})
    return render(request, 'login.html')

def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')

        if User.objects.filter(username=username).exists():
            return render(request, 'login.html', {'reg_error':'Username already exists'})
        
        User.objects.create_user(username=username, email=email, password=password)
        return redirect('login')
from django.contrib.auth.decorators import login_required
from .models import Booking

@login_required
def profile(request):
    bookings = Booking.objects.filter(user=request.user).order_by('-booking_date')
    return render(request, 'profile.html', {'bookings': bookings})

def custom_login(request):  # normal user
    if request.method == 'POST':
        u = request.POST.get('username')
        p = request.POST.get('password')
        user = authenticate(request, username=u, password=p)
        if user and not user.is_staff:
            login(request, user)
            return redirect('profile')
        return render(request,'login.html',{'error':'Invalid user login'})
    return render(request,'login.html')


def admin_login(request):
    if request.method == 'POST':
        u = request.POST.get('username')
        p = request.POST.get('password')

        user = authenticate(request, username=u, password=p)

        if user and (user.is_staff or user.is_superuser):
            login(request, user)
            return redirect('dashboard')

        return render(request, 'admin_login.html', {'error': 'You are not admin'})

    return render(request, 'admin_login.html')
