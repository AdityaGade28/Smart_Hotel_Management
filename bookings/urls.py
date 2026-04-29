from django.urls import path
from django.views.generic import RedirectView
from . import views

app_name = 'bookings'

urlpatterns = [
    path('hotel/<int:hotel_pk>/rooms/', views.hotel_rooms, name='hotel_rooms'),
    path('book/<int:room_pk>/', views.book_room, name='book_room'),
    path('my-bookings/', views.booking_list, name='booking_list'),
    path('booking_list/', RedirectView.as_view(pattern_name='bookings:booking_list', permanent=True)),
    path('<int:pk>/', views.booking_detail, name='booking_detail'),
    path('<int:pk>/cancel/', views.cancel_booking, name='cancel_booking'),
    path('<int:pk>/update-status/', views.admin_update_status, name='admin_update_status'),
    path('check-availability/', views.check_availability, name='check_availability'),
]
