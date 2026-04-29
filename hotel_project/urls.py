"""
URL configuration for hotel_project project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('hotels.urls', namespace='hotels')),
    path('users/', include('users.urls', namespace='users')),
    path('bookings/', include('bookings.urls', namespace='bookings')),
    path('food/', include('food_services.urls', namespace='food_services')),
    path('payments/', include('payments.urls', namespace='payments')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
