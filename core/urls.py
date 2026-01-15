from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views

urlpatterns = [
    # Public pages
    path('', views.home, name='home'),
    path('facilities/', views.facilities, name='facilities'),
    path('contact/', views.contact, name='contact'),
    path('map/', views.map_view, name='map'),

    # Booking
    path('book_room/', views.book_room, name='book_room'),

    # User Auth
    path('login/', views.custom_login, name='login'),
    path('register/', views.register, name='register'),
    path('profile/', views.profile, name='profile'),

    # Admin Auth
    path('admin-login/', views.admin_login, name='admin_login'),

    # Logout → Home
    path('logout/', LogoutView.as_view(next_page='home'), name='logout'),

    # Admin Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),
    path('bookings/', views.bookings, name='bookings'),
    path('payments/', views.payments, name='payments'),
    path('staff/', views.staff, name='staff'),
    path('invoice/<int:booking_id>/', views.invoice, name='invoice'),
]
