from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    RegisterView,
    LoginView,
    UserProfileView,
    ApplyTutorView,
    CustomTokenRefreshView,
    HealthCheckView
)

app_name = 'accounts'

urlpatterns = [
    # Public endpoints
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('token/refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),
    path('health/', HealthCheckView.as_view(), name='health_check'),
    
    # Protected endpoints (require authentication)
    path('profile/', UserProfileView.as_view(), name='profile'),
    path('apply-tutor/', ApplyTutorView.as_view(), name='apply_tutor'),
]