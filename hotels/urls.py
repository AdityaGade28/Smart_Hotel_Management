from django.urls import path
from . import views
from . import realtime_views

app_name = 'hotels'

urlpatterns = [
    # Public
    path('', views.home, name='home'),
    path('hotels/', views.hotel_list, name='hotel_list'),
    path('hotels/<int:pk>/', views.hotel_detail, name='hotel_detail'),
    path('hotels/map/', views.hotel_map, name='hotel_map'),

    # API (JSON for Leaflet map)
    path('api/hotels/', views.api_hotels, name='api_hotels'),
    path('api/hotels/recommend/', views.api_recommend, name='api_recommend'),

    # Real-time API endpoints (AJAX polling)
    path('api/realtime/admin-stats/', realtime_views.realtime_admin_stats, name='rt_admin_stats'),
    path('api/realtime/customer-stats/', realtime_views.realtime_customer_stats, name='rt_customer_stats'),
    path('api/realtime/room/<int:room_pk>/availability/', realtime_views.realtime_room_availability, name='rt_room_availability'),
    path('api/realtime/hotel/<int:hotel_pk>/stats/', realtime_views.realtime_hotel_stats, name='rt_hotel_stats'),
    path('api/realtime/notifications/', realtime_views.realtime_notifications, name='rt_notifications'),

    # Admin CRUD
    path('admin-hotels/', views.admin_hotel_list, name='admin_hotel_list'),
    path('admin-hotels/add/', views.admin_hotel_add, name='admin_hotel_add'),
    path('admin-hotels/<int:pk>/edit/', views.admin_hotel_edit, name='admin_hotel_edit'),
    path('admin-hotels/<int:pk>/delete/', views.admin_hotel_delete, name='admin_hotel_delete'),
    path('admin-rooms/', views.admin_room_list, name='admin_room_list'),
    path('admin-rooms/add/', views.admin_room_add, name='admin_room_add'),
    path('admin-rooms/<int:pk>/edit/', views.admin_room_edit, name='admin_room_edit'),
    path('admin-rooms/<int:pk>/delete/', views.admin_room_delete, name='admin_room_delete'),
]
