from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.utils import timezone

from .models import Booking, Subject
from .serializers import BookingSerializer, SubjectSerializer, BookingStatusUpdateSerializer
from .permissions import IsBookingOwner, IsTutorOrAdmin

class SubjectViewSet(viewsets.ModelViewSet):
    """ViewSet for subjects"""
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer
    permission_classes = [IsAuthenticated]
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsTutorOrAdmin()]
        return super().get_permissions()

class BookingViewSet(viewsets.ModelViewSet):
    """ViewSet for bookings"""
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        queryset = Booking.objects.select_related('student', 'tutor', 'subject')
        
        # Users can see their own bookings (as student or tutor)
        if not user.is_staff:
            queryset = queryset.filter(Q(student=user) | Q(tutor=user))
        
        # Filter by status if provided
        status_filter = self.request.query_params.get('status', None)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Filter by upcoming/past
        timeframe = self.request.query_params.get('timeframe', None)
        if timeframe == 'upcoming':
            queryset = queryset.filter(start_time__gte=timezone.now())
        elif timeframe == 'past':
            queryset = queryset.filter(start_time__lt=timezone.now())
        
        return queryset.order_by('-created_at')
    
    def perform_create(self, serializer):
        """Set the student to current user when creating booking"""
        serializer.save(student=self.request.user)
    
    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        """Update booking status"""
        booking = self.get_object()
        serializer = BookingStatusUpdateSerializer(data=request.data)
        
        if serializer.is_valid():
            status_value = serializer.validated_data['status']
            
            # Check permissions
            if status_value == 'cancelled':
                if booking.student != request.user and not request.user.is_staff:
                    return Response(
                        {'error': 'Only student or admin can cancel booking.'},
                        status=status.HTTP_403_FORBIDDEN
                    )
                booking.cancelled_by = request.user
                booking.cancellation_reason = serializer.validated_data.get('cancellation_reason', '')
            
            elif status_value in ['confirmed', 'completed', 'no_show']:
                if booking.tutor != request.user and not request.user.is_staff:
                    return Response(
                        {'error': 'Only tutor or admin can update to this status.'},
                        status=status.HTTP_403_FORBIDDEN
                    )
            
            booking.status = status_value
            booking.save()
            
            return Response(BookingSerializer(booking).data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def submit_feedback(self, request, pk=None):
        """Submit feedback for completed booking"""
        booking = self.get_object()
        
        if booking.status != 'completed':
            return Response(
                {'error': 'Feedback can only be submitted for completed bookings.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if booking.student != request.user:
            return Response(
                {'error': 'Only student can submit feedback.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        booking.student_rating = request.data.get('rating')
        booking.student_review = request.data.get('review', '')
        booking.save()
        
        return Response(BookingSerializer(booking).data)

class TutorAvailabilityViewSet(viewsets.ViewSet):
    """ViewSet for tutor availability"""
    permission_classes = [IsAuthenticated]
    
    def list(self, request):
        """Get available tutors"""
        from django.contrib.auth.models import User
        
        tutors = User.objects.filter(
            profile__tutor_approved=True
        ).select_related('profile')
        
        # Simple serialization
        data = []
        for tutor in tutors:
            data.append({
                'id': tutor.id,
                'name': f"{tutor.first_name} {tutor.last_name}",
                'email': tutor.email,
                'academic_year': tutor.profile.academic_year,
            })
        
        return Response(data)