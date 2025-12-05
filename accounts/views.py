from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User
from django.utils import timezone
from .serializers import (
    UserRegistrationSerializer, 
    UserLoginSerializer,
    UserProfileSerializer,
    TutorApplicationSerializer
)
from .permissions import IsOwnerOrReadOnly
import logging

logger = logging.getLogger(__name__)

class RegisterView(APIView):
    """View for user registration"""
    permission_classes = [AllowAny]
    
    def post(self, request):
        """Register a new user"""
        try:
            serializer = UserRegistrationSerializer(data=request.data)
            
            if not serializer.is_valid():
                return Response(
                    {"errors": serializer.errors},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            user = serializer.save()
            
            # Generate tokens for immediate login
            refresh = RefreshToken.for_user(user)
            
            # Get user profile data
            profile_serializer = UserProfileSerializer(user.profile)
            
            return Response({
                "message": "Registration successful",
                "user": profile_serializer.data,
                "tokens": {
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                }
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            logger.error(f"Registration error: {str(e)}")
            return Response(
                {"error": "An error occurred during registration. Please try again."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class LoginView(APIView):
    """View for user login"""
    permission_classes = [AllowAny]
    
    def post(self, request):
        """Authenticate user and return tokens"""
        try:
            serializer = UserLoginSerializer(data=request.data)
            
            if not serializer.is_valid():
                return Response(
                    {"errors": serializer.errors},
                    status=status.HTTP_401_UNAUTHORIZED
                )
            
            user = serializer.validated_data['user']
            
            # Generate tokens
            refresh = RefreshToken.for_user(user)
            
            # Get user profile data
            profile_serializer = UserProfileSerializer(user.profile)
            
            return Response({
                "message": "Login successful",
                "user": profile_serializer.data,
                "tokens": {
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                }
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Login error: {str(e)}")
            return Response(
                {"error": "An error occurred during login. Please try again."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class UserProfileView(APIView):
    """View for user profile management"""
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    
    def get(self, request):
        """Get user profile"""
        try:
            user = request.user
            serializer = UserProfileSerializer(user.profile)
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Get profile error: {str(e)}")
            return Response(
                {"error": "Failed to retrieve profile."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def put(self, request):
        """Update user profile"""
        try:
            user = request.user
            serializer = UserProfileSerializer(
                user.profile, 
                data=request.data, 
                partial=True
            )
            
            if not serializer.is_valid():
                return Response(
                    {"errors": serializer.errors},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            serializer.save()
            return Response({
                "message": "Profile updated successfully",
                "profile": serializer.data
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Update profile error: {str(e)}")
            return Response(
                {"error": "Failed to update profile."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def patch(self, request):
        """Partial update user profile"""
        return self.put(request)

class ApplyTutorView(APIView):
    """View for applying to become a tutor"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """Submit tutor application"""
        try:
            user = request.user
            
            # Validate application
            serializer = TutorApplicationSerializer(
                data={}, 
                context={'request': request}
            )
            
            if not serializer.is_valid():
                return Response(
                    {"errors": serializer.errors},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Apply as tutor
            profile = user.profile
            if profile.apply_as_tutor():
                # Send notification (console output for now)
                print(f"\n=== TUTOR APPLICATION ===\n"
                      f"User: {user.email}\n"
                      f"Name: {user.get_full_name()}\n"
                      f"Academic Year: {profile.academic_year}\n"
                      f"Applied at: {profile.tutor_application_date}\n"
                      f"Please review in admin panel.\n")
                
                return Response({
                    "message": "Tutor application submitted successfully!",
                    "application_date": profile.tutor_application_date.strftime('%Y-%m-%d %H:%M:%S'),
                    "status": "pending_admin_approval"
                }, status=status.HTTP_200_OK)
            else:
                return Response(
                    {"error": "Failed to submit tutor application."},
                    status=status.HTTP_400_BAD_REQUEST
                )
                
        except Exception as e:
            logger.error(f"Tutor application error: {str(e)}")
            return Response(
                {"error": "An error occurred while submitting your application."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class CustomTokenRefreshView(TokenRefreshView):
    """Custom token refresh view with error handling"""
    
    def post(self, request, *args, **kwargs):
        try:
            return super().post(request, *args, **kwargs)
        except Exception as e:
            logger.error(f"Token refresh error: {str(e)}")
            return Response(
                {"error": "Failed to refresh token. Please login again."},
                status=status.HTTP_401_UNAUTHORIZED
            )

class HealthCheckView(APIView):
    """Health check endpoint"""
    permission_classes = [AllowAny]
    
    def get(self, request):
        return Response({
            "status": "healthy",
            "service": "accounts",
            "timestamp": timezone.now().isoformat()
        }, status=status.HTTP_200_OK)