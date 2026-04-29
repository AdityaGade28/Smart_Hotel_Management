from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from bookings.models import Booking
from .models import MenuItem, Order, OrderItem, ServiceRequest


@login_required
def menu_view(request, booking_pk):
    booking = get_object_or_404(Booking, pk=booking_pk, customer=request.user)
    menu_items = MenuItem.objects.filter(is_available=True)
    categories = {}
    for item in menu_items:
        cat = item.get_category_display()
        categories.setdefault(cat, []).append(item)
    return render(request, 'food_services/menu.html', {
        'booking': booking, 'categories': categories
    })


@login_required
def place_order(request, booking_pk):
    booking = get_object_or_404(Booking, pk=booking_pk, customer=request.user)
    if request.method == 'POST':
        item_ids = request.POST.getlist('items[]')
        quantities = request.POST.getlist('quantities[]')
        notes = request.POST.get('notes', '')

        if not item_ids:
            messages.error(request, 'Please select at least one item.')
            return redirect('food_services:menu', booking_pk=booking_pk)

        order = Order.objects.create(booking=booking, notes=notes)
        total = 0
        for item_id, qty in zip(item_ids, quantities):
            try:
                item = MenuItem.objects.get(pk=item_id, is_available=True)
                qty = int(qty) if int(qty) > 0 else 1
                OrderItem.objects.create(order=order, menu_item=item, quantity=qty)
                total += item.price * qty
            except (MenuItem.DoesNotExist, ValueError):
                pass

        order.total = total
        order.save()
        messages.success(request, f'Order #{order.pk} placed! We\'ll deliver to your room shortly.')
        return redirect('food_services:order_status', booking_pk=booking_pk)
    return redirect('food_services:menu', booking_pk=booking_pk)


@login_required
def order_status(request, booking_pk):
    booking = get_object_or_404(Booking, pk=booking_pk, customer=request.user)
    orders = booking.food_orders.all().prefetch_related('orderitem_set__menu_item')
    return render(request, 'food_services/order_status.html', {
        'booking': booking, 'orders': orders
    })


@login_required
def request_service(request, booking_pk):
    booking = get_object_or_404(Booking, pk=booking_pk, customer=request.user)
    if request.method == 'POST':
        service_type = request.POST.get('service_type')
        notes = request.POST.get('notes', '')
        if service_type:
            ServiceRequest.objects.create(booking=booking, service_type=service_type, notes=notes)
            messages.success(request, 'Service request submitted! Our team will attend shortly.')
        return redirect('food_services:my_services', booking_pk=booking_pk)
    service_choices = ServiceRequest.SERVICE_CHOICES
    return render(request, 'food_services/request_service.html', {
        'booking': booking, 'service_choices': service_choices
    })


@login_required
def my_services(request, booking_pk):
    booking = get_object_or_404(Booking, pk=booking_pk, customer=request.user)
    services = booking.service_requests.all()
    return render(request, 'food_services/my_services.html', {
        'booking': booking, 'services': services
    })


# Admin views
@login_required
def admin_orders(request):
    if not request.user.is_admin_user():
        messages.error(request, 'Access denied.')
        return redirect('hotels:home')
    orders = Order.objects.select_related('booking__customer').prefetch_related('orderitem_set__menu_item').all()
    return render(request, 'food_services/admin/orders.html', {'orders': orders})


@login_required
def admin_update_order(request, pk):
    if not request.user.is_admin_user():
        messages.error(request, 'Access denied.')
        return redirect('hotels:home')
    order = get_object_or_404(Order, pk=pk)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in ['pending', 'preparing', 'delivered', 'cancelled']:
            order.status = new_status
            order.save()
            messages.success(request, f'Order #{order.pk} status updated to {new_status}.')
    return redirect('food_services:admin_orders')


@login_required
def admin_services(request):
    if not request.user.is_admin_user():
        messages.error(request, 'Access denied.')
        return redirect('hotels:home')
    services = ServiceRequest.objects.select_related('booking__customer').all()
    return render(request, 'food_services/admin/services.html', {'services': services})


@login_required
def admin_update_service(request, pk):
    if not request.user.is_admin_user():
        messages.error(request, 'Access denied.')
        return redirect('hotels:home')
    service = get_object_or_404(ServiceRequest, pk=pk)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in ['pending', 'in_progress', 'completed', 'cancelled']:
            service.status = new_status
            service.save()
            messages.success(request, f'Service request updated to {new_status}.')
    return redirect('food_services:admin_services')


@login_required
def admin_menu(request):
    if not request.user.is_admin_user():
        messages.error(request, 'Access denied.')
        return redirect('hotels:home')
    items = MenuItem.objects.all()
    return render(request, 'food_services/admin/menu_list.html', {'items': items})


@login_required
def admin_menu_toggle(request, pk):
    if not request.user.is_admin_user():
        messages.error(request, 'Access denied.')
        return redirect('hotels:home')
    item = get_object_or_404(MenuItem, pk=pk)
    item.is_available = not item.is_available
    item.save()
    messages.success(request, f'Menu item "{item.name}" availability updated.')
    return redirect('food_services:admin_menu')
