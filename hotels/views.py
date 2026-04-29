from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q, Min
from .models import Hotel, Room
from .forms import HotelForm, RoomForm, HotelFilterForm
from .recommendation import get_recommended_hotel, get_hotels_with_scores


def home(request):
    hotels = Hotel.objects.filter(is_active=True)
    featured_hotels = hotels.order_by('-rating')[:6]
    recommended_hotel, rec_score = get_recommended_hotel(hotels)
    context = {
        'featured_hotels': featured_hotels,
        'recommended_hotel': recommended_hotel,
        'rec_score': rec_score,
        'total_hotels': hotels.count(),
    }
    return render(request, 'hotels/home.html', context)


def hotel_list(request):
    hotels = Hotel.objects.filter(is_active=True)
    form = HotelFilterForm(request.GET)
    recommended_hotel, _ = get_recommended_hotel(hotels)

    if form.is_valid():
        city = form.cleaned_data.get('city')
        min_price = form.cleaned_data.get('min_price')
        max_price = form.cleaned_data.get('max_price')
        min_rating = form.cleaned_data.get('min_rating')
        sort_by = form.cleaned_data.get('sort_by')

        if city:
            hotels = hotels.filter(Q(city__icontains=city) | Q(name__icontains=city))
        if min_rating:
            hotels = hotels.filter(rating__gte=min_rating)
        if min_price:
            hotels = hotels.filter(rooms__price_per_night__gte=min_price)
        if max_price:
            hotels = hotels.filter(rooms__price_per_night__lte=max_price)
        if sort_by == 'rating':
            hotels = hotels.order_by('-rating')
        elif sort_by == 'price_asc':
            hotels = hotels.annotate(min_price=Min('rooms__price_per_night')).order_by('min_price')
        elif sort_by == 'price_desc':
            hotels = hotels.annotate(min_price=Min('rooms__price_per_night')).order_by('-min_price')

    hotels = hotels.distinct()
    hotels_scored = get_hotels_with_scores(hotels)

    context = {
        'hotels_scored': hotels_scored,
        'recommended_hotel': recommended_hotel,
        'form': form,
        'total': hotels.count(),
    }
    return render(request, 'hotels/hotel_list.html', context)


def hotel_detail(request, pk):
    hotel = get_object_or_404(Hotel, pk=pk, is_active=True)
    rooms = hotel.rooms.all()
    available_rooms = rooms.filter(is_available=True)
    context = {
        'hotel': hotel,
        'rooms': rooms,
        'available_rooms': available_rooms,
    }
    return render(request, 'hotels/hotel_detail.html', context)


def hotel_map(request):
    hotels = Hotel.objects.filter(is_active=True)
    recommended_hotel, rec_score = get_recommended_hotel(hotels)
    context = {
        'hotels': hotels,
        'recommended_hotel': recommended_hotel,
    }
    return render(request, 'hotels/hotel_map.html', context)


# ─── JSON API for Leaflet map ────────────────────────────────────────────────

def api_hotels(request):
    hotels = Hotel.objects.filter(is_active=True)
    recommended_hotel, _ = get_recommended_hotel(hotels)

    # Filters
    city = request.GET.get('city', '')
    min_rating = request.GET.get('min_rating', '')
    available_only = request.GET.get('available_only', '')

    if city:
        hotels = hotels.filter(Q(city__icontains=city) | Q(name__icontains=city))
    if min_rating:
        try:
            hotels = hotels.filter(rating__gte=float(min_rating))
        except ValueError:
            pass
    if available_only:
        hotels = hotels.filter(rooms__is_available=True).distinct()

    data = []
    for hotel in hotels:
        data.append({
            'id': hotel.id,
            'name': hotel.name,
            'city': hotel.city,
            'latitude': float(hotel.latitude),
            'longitude': float(hotel.longitude),
            'rating': float(hotel.rating),
            'available_rooms': hotel.get_available_rooms(),
            'min_price': float(hotel.get_min_price()) if hotel.get_min_price() else None,
            'image': hotel.image.url if hotel.image else None,
            'is_recommended': recommended_hotel and hotel.id == recommended_hotel.id,
            'score': hotel.recommendation_score(),
            'detail_url': f'/hotels/{hotel.id}/',
            'book_url': f'/bookings/hotel/{hotel.id}/rooms/',
        })
    return JsonResponse({'hotels': data})


def api_recommend(request):
    hotels = Hotel.objects.filter(is_active=True)
    recommended, score = get_recommended_hotel(hotels)
    if recommended:
        return JsonResponse({
            'hotel_id': recommended.id,
            'hotel_name': recommended.name,
            'score': score,
        })
    return JsonResponse({'hotel_id': None, 'hotel_name': None, 'score': 0})


# ─── Admin CRUD Views ────────────────────────────────────────────────────────

@login_required
def admin_hotel_list(request):
    if not request.user.is_admin_user():
        messages.error(request, 'Access denied.')
        return redirect('hotels:home')
    hotels = Hotel.objects.all()
    return render(request, 'hotels/admin/hotel_list.html', {'hotels': hotels})


@login_required
def admin_hotel_add(request):
    if not request.user.is_admin_user():
        messages.error(request, 'Access denied.')
        return redirect('hotels:home')
    if request.method == 'POST':
        form = HotelForm(request.POST, request.FILES)
        if form.is_valid():
            hotel = form.save()
            messages.success(request, f'Hotel "{hotel.name}" added successfully!')
            return redirect('hotels:admin_hotel_list')
    else:
        form = HotelForm()
    return render(request, 'hotels/admin/hotel_form.html', {'form': form, 'title': 'Add Hotel'})


@login_required
def admin_hotel_edit(request, pk):
    if not request.user.is_admin_user():
        messages.error(request, 'Access denied.')
        return redirect('hotels:home')
    hotel = get_object_or_404(Hotel, pk=pk)
    if request.method == 'POST':
        form = HotelForm(request.POST, request.FILES, instance=hotel)
        if form.is_valid():
            form.save()
            messages.success(request, f'Hotel "{hotel.name}" updated successfully!')
            return redirect('hotels:admin_hotel_list')
    else:
        form = HotelForm(instance=hotel)
    return render(request, 'hotels/admin/hotel_form.html', {'form': form, 'title': 'Edit Hotel', 'hotel': hotel})


@login_required
def admin_hotel_delete(request, pk):
    if not request.user.is_admin_user():
        messages.error(request, 'Access denied.')
        return redirect('hotels:home')
    hotel = get_object_or_404(Hotel, pk=pk)
    if request.method == 'POST':
        name = hotel.name
        hotel.delete()
        messages.success(request, f'Hotel "{name}" deleted.')
        return redirect('hotels:admin_hotel_list')
    return render(request, 'hotels/admin/hotel_confirm_delete.html', {'hotel': hotel})


@login_required
def admin_room_list(request):
    if not request.user.is_admin_user():
        messages.error(request, 'Access denied.')
        return redirect('hotels:home')
    hotel_id = request.GET.get('hotel')
    rooms = Room.objects.select_related('hotel').all()
    hotels = Hotel.objects.all()
    if hotel_id:
        rooms = rooms.filter(hotel_id=hotel_id)
    return render(request, 'hotels/admin/room_list.html', {'rooms': rooms, 'hotels': hotels})


@login_required
def admin_room_add(request):
    if not request.user.is_admin_user():
        messages.error(request, 'Access denied.')
        return redirect('hotels:home')
    if request.method == 'POST':
        form = RoomForm(request.POST, request.FILES)
        if form.is_valid():
            room = form.save()
            messages.success(request, f'Room {room.room_number} added successfully!')
            return redirect('hotels:admin_room_list')
    else:
        initial = {}
        hotel_id = request.GET.get('hotel')
        if hotel_id:
            initial['hotel'] = hotel_id
        form = RoomForm(initial=initial)
    return render(request, 'hotels/admin/room_form.html', {'form': form, 'title': 'Add Room'})


@login_required
def admin_room_edit(request, pk):
    if not request.user.is_admin_user():
        messages.error(request, 'Access denied.')
        return redirect('hotels:home')
    room = get_object_or_404(Room, pk=pk)
    if request.method == 'POST':
        form = RoomForm(request.POST, request.FILES, instance=room)
        if form.is_valid():
            form.save()
            messages.success(request, f'Room {room.room_number} updated!')
            return redirect('hotels:admin_room_list')
    else:
        form = RoomForm(instance=room)
    return render(request, 'hotels/admin/room_form.html', {'form': form, 'title': 'Edit Room', 'room': room})


@login_required
def admin_room_delete(request, pk):
    if not request.user.is_admin_user():
        messages.error(request, 'Access denied.')
        return redirect('hotels:home')
    room = get_object_or_404(Room, pk=pk)
    if request.method == 'POST':
        room_num = room.room_number
        hotel_name = room.hotel.name
        room.delete()
        messages.success(request, f'Room {room_num} from {hotel_name} deleted.')
        return redirect('hotels:admin_room_list')
    return render(request, 'hotels/admin/room_confirm_delete.html', {'room': room})
