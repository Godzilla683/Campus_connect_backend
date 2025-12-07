from rest_framework import serializers
from .models import Booking, Subject
from django.contrib.auth.models import User

class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = ('id', 'name', 'code', 'description')
        read_only_fields = ('id',)

class SimpleUserSerializer(serializers.ModelSerializer):
    """Simple user serializer for booking display"""
    full_name = serializers.SerializerMethodField()
    academic_year = serializers.CharField(source='profile.academic_year', read_only=True)
    
    class Meta:
        model = User
        fields = ('id', 'email', 'full_name', 'academic_year')
        read_only_fields = ('id', 'email', 'full_name', 'academic_year')
    
    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip()

class BookingSerializer(serializers.ModelSerializer):
    """Serializer for bookings"""
    student = SimpleUserSerializer(read_only=True)
    tutor = SimpleUserSerializer(read_only=True)
    student_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        write_only=True,
        source='student'
    )
    tutor_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(profile__tutor_approved=True),
        write_only=True,
        source='tutor'
    )
    subject_id = serializers.PrimaryKeyRelatedField(
        queryset=Subject.objects.all(),
        write_only=True,
        source='subject',
        required=False,
        allow_null=True
    )
    subject = SubjectSerializer(read_only=True)
    
    class Meta:
        model = Booking
        fields = (
            'id', 'student', 'tutor', 'subject', 'subject_id',
            'topic', 'description', 'duration_minutes',
            'start_time', 'end_time', 'location', 'is_virtual',
            'meeting_link', 'status', 'hourly_rate', 'total_amount',
            'is_paid', 'student_id', 'tutor_id',
            'student_rating', 'student_review', 'created_at'
        )
        read_only_fields = (
            'id', 'student', 'tutor', 'subject', 'status', 
            'total_amount', 'is_paid', 'created_at'
        )
    
    def validate(self, data):
        """Validate booking data"""
        if data['student'] == data['tutor']:
            raise serializers.ValidationError("Student and tutor cannot be the same person.")
        
        # Check if tutor is available (simple check - can be enhanced later)
        existing_booking = Booking.objects.filter(
            tutor=data['tutor'],
            start_time__lt=data.get('end_time', data['start_time']),
            end_time__gt=data['start_time'],
            status__in=['pending', 'confirmed']
        ).exists()
        
        if existing_booking:
            raise serializers.ValidationError("Tutor is not available at this time.")
        
        return data

class BookingStatusUpdateSerializer(serializers.Serializer):
    """Serializer for updating booking status"""
    status = serializers.ChoiceField(choices=Booking.STATUS_CHOICES)
    cancellation_reason = serializers.CharField(required=False, allow_blank=True)