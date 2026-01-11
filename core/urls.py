from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Public pages
    path('', views.home, name='home'),
    path('facilities/', views.facilities, name='facilities'),
    path('contact/', views.contact, name='contact'),
    path('book_room/', views.book_room, name='book_room'),

    # User authentication
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
     path('login/', views.custom_login, name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    # Admin authentication
   # path('admin_login/', auth_views.LoginView.as_view(template_name='admin_login.html'), name='admin_login'),

    # Admin dashboard pages
    path('dashboard/', views.dashboard, name='dashboard'),
    path('bookings/', views.bookings, name='bookings'),
    path('payments/', views.payments, name='payments'),
    path('staff/', views.staff, name='staff'),
    path('invoice/', views.invoice, name='invoice'),
    
    path('invoice/<int:booking_id>/', views.invoice, name='invoice'),
    path('login/', views.custom_login, name='login'),
        path('admin_login/', auth_views.LoginView.as_view(template_name='admin_login.html'), name='admin_login'),
    path('dashboard/', views.dashboard, name='dashboard'),

]

