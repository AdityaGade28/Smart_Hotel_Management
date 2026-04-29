from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Count, Q
from django.utils import timezone
from .models import CustomUser, Profile
from .forms import RegisterForm, LoginForm, ProfileUpdateForm


def register_view(request):
    if request.user.is_authenticated:
        return redirect('hotels:home')
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.role = form.cleaned_data['role']
            user.phone = form.cleaned_data.get('phone', '')
            if user.role == 'admin':
                user.is_staff = True
            user.save()
            Profile.objects.create(user=user)
            login(request, user)
            messages.success(request, f'Welcome, {user.username}! Your account has been created.')
            if user.is_admin_user():
                return redirect('users:admin_dashboard')
            return redirect('hotels:home')
    else:
        form = RegisterForm()
    return render(request, 'users/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('hotels:home')
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            next_url = request.GET.get('next', '')
            if next_url:
                return redirect(next_url)
            if user.is_admin_user():
                return redirect('users:admin_dashboard')
            return redirect('users:customer_dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = LoginForm(request)
    return render(request, 'users/login.html', {'form': form})


@login_required
def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('users:login')


@login_required
def customer_dashboard(request):
    if request.user.is_admin_user():
        return redirect('users:admin_dashboard')
    from bookings.models import Booking
    bookings = Booking.objects.filter(customer=request.user).order_by('-created_at')[:5]
    total_bookings = Booking.objects.filter(customer=request.user).count()
    active_bookings = Booking.objects.filter(customer=request.user, status='confirmed').count()
    cancelled_bookings = Booking.objects.filter(customer=request.user, status='cancelled').count()
    context = {
        'bookings': bookings,
        'total_bookings': total_bookings,
        'active_bookings': active_bookings,
        'cancelled_bookings': cancelled_bookings,
    }
    return render(request, 'users/dashboard_customer.html', context)


@login_required
def admin_dashboard(request):
    if not request.user.is_admin_user():
        messages.error(request, 'Access denied. Admin only.')
        return redirect('users:customer_dashboard')

    from bookings.models import Booking
    from hotels.models import Hotel, Room
    from payments.models import Payment

    total_hotels = Hotel.objects.count()
    total_rooms = Room.objects.count()
    available_rooms = Room.objects.filter(is_available=True).count()
    total_users = CustomUser.objects.filter(role='customer').count()
    total_bookings = Booking.objects.count()
    confirmed_bookings = Booking.objects.filter(status='confirmed').count()
    pending_bookings = Booking.objects.filter(status='pending').count()
    cancelled_bookings = Booking.objects.filter(status='cancelled').count()

    total_revenue = Payment.objects.filter(status='completed').aggregate(
        total=Sum('amount')
    )['total'] or 0

    occupancy_rate = 0
    if total_rooms > 0:
        occupancy_rate = round(((total_rooms - available_rooms) / total_rooms) * 100, 1)

    recent_bookings = Booking.objects.order_by('-created_at')[:10]

    # Monthly revenue for chart (last 6 months)
    try:
        from django.db.models.functions import TruncMonth
        monthly_revenue = list(
            Payment.objects.filter(status='completed')
            .annotate(month=TruncMonth('created_at'))
            .values('month')
            .annotate(total=Sum('amount'))
            .order_by('month')
        )[:6]
    except Exception:
        # Fallback if DB aggregation fails (common on Windows/MySQL local setups)
        monthly_revenue = []

    context = {
        'total_hotels': total_hotels,
        'total_rooms': total_rooms,
        'available_rooms': available_rooms,
        'total_users': total_users,
        'total_bookings': total_bookings,
        'confirmed_bookings': confirmed_bookings,
        'pending_bookings': pending_bookings,
        'cancelled_bookings': cancelled_bookings,
        'total_revenue': total_revenue,
        'occupancy_rate': occupancy_rate,
        'recent_bookings': recent_bookings,
        'monthly_revenue': monthly_revenue,
    }
    return render(request, 'users/dashboard_admin.html', context)


@login_required
def profile_view(request):
    profile, created = Profile.objects.get_or_create(user=request.user)
    return render(request, 'users/profile.html', {'profile': profile})


@login_required
def profile_edit_view(request):
    profile, created = Profile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            # Update user fields
            request.user.first_name = form.cleaned_data.get('first_name', '')
            request.user.last_name = form.cleaned_data.get('last_name', '')
            request.user.email = form.cleaned_data.get('email', '')
            request.user.phone = form.cleaned_data.get('phone', '')
            request.user.save()
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('users:profile')
    else:
        form = ProfileUpdateForm(instance=profile)
    return render(request, 'users/profile_edit.html', {'form': form})


@login_required
def manage_users(request):
    if not request.user.is_admin_user():
        messages.error(request, 'Access denied.')
        return redirect('hotels:home')
    users = CustomUser.objects.all().order_by('-date_joined')
    return render(request, 'users/manage_users.html', {'users': users})


@login_required
def toggle_user_status(request, pk):
    if not request.user.is_admin_user():
        messages.error(request, 'Access denied.')
        return redirect('hotels:home')
    user = get_object_or_404(CustomUser, pk=pk)
    if user != request.user:
        user.is_active = not user.is_active
        user.save()
        status = 'activated' if user.is_active else 'deactivated'
        messages.success(request, f'User {user.username} has been {status}.')
    return redirect('users:manage_users')
