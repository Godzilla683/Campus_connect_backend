from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SubjectViewSet, BookingViewSet, TutorAvailabilityViewSet

router = DefaultRouter()
router.register(r'subjects', SubjectViewSet, basename='subject')
router.register(r'bookings', BookingViewSet, basename='booking')
router.register(r'tutors', TutorAvailabilityViewSet, basename='tutor')

app_name = 'bookings'

urlpatterns = [
    path('', include(router.urls)),
]