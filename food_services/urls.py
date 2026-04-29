from django.urls import path
from . import views

app_name = 'food_services'

urlpatterns = [
    path('<int:booking_pk>/menu/', views.menu_view, name='menu'),
    path('<int:booking_pk>/order/', views.place_order, name='place_order'),
    path('<int:booking_pk>/order-status/', views.order_status, name='order_status'),
    path('<int:booking_pk>/services/', views.request_service, name='request_service'),
    path('<int:booking_pk>/my-services/', views.my_services, name='my_services'),
    # Admin
    path('admin/orders/', views.admin_orders, name='admin_orders'),
    path('admin/orders/<int:pk>/update/', views.admin_update_order, name='admin_update_order'),
    path('admin/services/', views.admin_services, name='admin_services'),
    path('admin/services/<int:pk>/update/', views.admin_update_service, name='admin_update_service'),
    path('admin/menu/', views.admin_menu, name='admin_menu'),
    path('admin/menu/<int:pk>/toggle/', views.admin_menu_toggle, name='admin_menu_toggle'),
]
