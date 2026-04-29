from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('checkout/<int:booking_pk>/', views.checkout, name='checkout'),
    path('verify-payment/', views.verify_payment, name='verify_payment'),
    path('success/<int:pk>/', views.payment_success, name='payment_success'),
    path('failed/<int:pk>/', views.payment_failed, name='payment_failed'),
    path('history/', views.payment_history, name='payment_history'),
]
