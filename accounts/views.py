from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User
from django.utils import timezone

from .serializers import (
    UserRegistrationSerializer, 
    UserLoginSerializer,
    UserProfileSerializer,
    TutorApplicationSerializer,
    UserSerializer
)
from .permissions import IsOwnerOrReadOnly

class RegisterView(APIView):
    """View for user registration"""
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(
                {"errors": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user = serializer.save()
        
        # Generate tokens for immediate login
        refresh = RefreshToken.for_user(user)
        
        return Response({
            "message": "Registration successful",
            "tokens": {
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            }
        }, status=status.HTTP_201_CREATED)

class LoginView(APIView):
    """View for user login"""
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(
                {"errors": serializer.errors},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        user = serializer.validated_data['user']
        
        # Generate tokens
        refresh = RefreshToken.for_user(user)
        
        return Response({
            "message": "Login successful",
            "tokens": {
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            }
        }, status=status.HTTP_200_OK)

class UserProfileView(APIView):
    """View for user profile management"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get user profile"""
        serializer = UserProfileSerializer(request.user.profile)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def put(self, request):
        """Update user profile"""
        serializer = UserProfileSerializer(
            request.user.profile, 
            data=request.data, 
            partial=True
        )
        
        if not serializer.is_valid():
            return Response(
                {"errors": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def patch(self, request):
        """Partial update user profile"""
        return self.put(request)

class ApplyTutorView(APIView):
    """View for applying to become a tutor"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """Submit tutor application"""
        serializer = TutorApplicationSerializer(
            data=request.data,
            context={'request': request}
        )
        
        if not serializer.is_valid():
            return Response(
                {"errors": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        profile = serializer.save()
        
        return Response({
            "message": "Tutor application submitted successfully!",
            "application_date": profile.tutor_application_date.strftime('%Y-%m-%d'),
            "status": "pending_admin_approval"
        }, status=status.HTTP_200_OK)

class LogoutView(APIView):
    """View for user logout"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        return Response({
            "message": "Logged out successfully"
        }, status=status.HTTP_200_OK)

class HealthCheckView(APIView):
    """Health check endpoint"""
    permission_classes = [AllowAny]
    
    def get(self, request):
        return Response({
            "status": "healthy",
            "timestamp": timezone.now().isoformat()
        }, status=status.HTTP_200_OK)

# Admin views (optional for MVP)
class TutorApplicationsView(APIView):
    """View for admin to manage tutor applications"""
    permission_classes = [IsAdminUser]
    
    def get(self, request):
        """Get all pending tutor applications"""
        from .models import UserProfile
        
        pending_applications = UserProfile.objects.filter(
            is_tutor=True,
            tutor_approved=False
        ).select_related('user')
        
        serializer = UserProfileSerializer(pending_applications, many=True)
        
        return Response({
            "applications": serializer.data
        }, status=status.HTTP_200_OK)
    
    def post(self, request, user_id=None):
        """Approve/reject tutor application (admin only)"""
        from django.shortcuts import get_object_or_404
        
        user = get_object_or_404(User, id=user_id or request.data.get('user_id'))
        profile = user.profile
        
        if not profile.is_tutor:
            return Response(
                {"error": "User has not applied to be a tutor."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        action = request.data.get('action', 'approve')
        
        if action == 'approve':
            profile.tutor_approved = True
            profile.save()
            message = "Tutor application approved."
        else:
            profile.is_tutor = False
            profile.tutor_application_date = None
            profile.save()
            message = "Tutor application rejected."
        
        return Response({
            "message": message,
            "profile": UserProfileSerializer(profile).data
        }, status=status.HTTP_200_OK)

class UserListView(APIView):
    """View for listing users (admin only)"""
    permission_classes = [IsAdminUser]
    
    def get(self, request):
        """Get all users"""
        users = User.objects.all().select_related('profile')
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)