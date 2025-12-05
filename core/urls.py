from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('accounts.urls')),
    path('documents/', include('documents.urls')),
    path('bookings/', include('bookings.urls')),
    path('', include('pages.urls')),
]
