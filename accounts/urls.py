from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    RegisterView,
    LoginView,
    UserProfileView,
    ApplyTutorView,
    LogoutView,
    HealthCheckView,
    # Admin views kept simple
    TutorApplicationsView,
    UserListView,
)

app_name = 'accounts'

urlpatterns = [
    # Public endpoints
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('health/', HealthCheckView.as_view(), name='health_check'),
    
    # Authenticated endpoints
    path('profile/', UserProfileView.as_view(), name='profile'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('apply-tutor/', ApplyTutorView.as_view(), name='apply_tutor'),
    
    # Admin endpoints (minimal)
    path('admin/users/', UserListView.as_view(), name='user_list'),
    path('admin/tutor-applications/', TutorApplicationsView.as_view(), name='tutor_applications'),
]