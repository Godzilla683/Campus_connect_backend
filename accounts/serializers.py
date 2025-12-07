from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from .models import UserProfile

class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration"""
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, required=True, min_length=8)
    password2 = serializers.CharField(write_only=True, required=True)
    academic_year = serializers.ChoiceField(
        choices=UserProfile.ACADEMIC_YEAR_CHOICES, 
        required=True
    )
    
    class Meta:
        model = User
        fields = ('email', 'password', 'password2', 'first_name', 'last_name', 'academic_year')
    
    def validate_email(self, value):
        """Validate email"""
        value = value.lower().strip()
        
        # Basic email validation
        if not '@' in value:
            raise serializers.ValidationError("Enter a valid email address.")
        
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        
        return value
    
    def validate_password(self, value):
        """Basic password validation"""
        if len(value) < 8:
            raise serializers.ValidationError("Password must be at least 8 characters long.")
        return value
    
    def validate(self, data):
        """Validate passwords match"""
        if data['password'] != data['password2']:
            raise serializers.ValidationError({"password2": "Passwords do not match."})
        
        # Remove password2 from validated data
        data.pop('password2')
        return data
    
    def create(self, validated_data):
        """Create user and user profile"""
        # Extract academic_year from validated_data
        academic_year = validated_data.pop('academic_year')
        
        # Create user with email as username
        user = User.objects.create_user(
            username=validated_data['email'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name']
        )
        
        # Update profile with academic year
        user.profile.academic_year = academic_year
        user.profile.save()
        
        return user

class UserLoginSerializer(serializers.Serializer):
    """Serializer for user login"""
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, required=True)
    
    def validate(self, data):
        """Validate user credentials"""
        email = data.get('email', '').lower().strip()
        password = data.get('password', '')
        
        if not email or not password:
            raise serializers.ValidationError("Both email and password are required.")
        
        # Find user by email
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError("Invalid email or password.")
        
        # Check if user is active
        if not user.is_active:
            raise serializers.ValidationError("This account is inactive.")
        
        # Authenticate user
        user = authenticate(username=user.username, password=password)
        if not user:
            raise serializers.ValidationError("Invalid email or password.")
        
        data['user'] = user
        return data

class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for user profile"""
    email = serializers.EmailField(source='user.email', read_only=True)
    first_name = serializers.CharField(source='user.first_name', required=False)
    last_name = serializers.CharField(source='user.last_name', required=False)
    
    class Meta:
        model = UserProfile
        fields = (
            'id', 'email', 'first_name', 'last_name',
            'academic_year', 'is_tutor', 'tutor_approved', 
            'tutor_application_date', 'date_joined'
        )
        read_only_fields = (
            'id', 'email', 'is_tutor', 'tutor_approved', 
            'tutor_application_date', 'date_joined'
        )
    
    def update(self, instance, validated_data):
        """Update user and profile"""
        # Extract user data if present
        user_data = validated_data.pop('user', {})
        
        # Update user fields
        user = instance.user
        if 'first_name' in user_data:
            user.first_name = user_data['first_name']
        if 'last_name' in user_data:
            user.last_name = user_data['last_name']
        user.save()
        
        # Update profile fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        instance.save()
        return instance

class TutorApplicationSerializer(serializers.Serializer):
    """Serializer for tutor application"""
    
    def validate(self, data):
        """Validate user can apply as tutor"""
        user = self.context['request'].user
        
        if not user.is_authenticated:
            raise serializers.ValidationError("Authentication required.")
        
        profile = user.profile
        
        if profile.tutor_approved:
            raise serializers.ValidationError("You are already an approved tutor.")
        
        if profile.is_tutor and profile.tutor_application_date:
            raise serializers.ValidationError(
                f"You already applied on {profile.tutor_application_date.strftime('%Y-%m-%d')}. "
                "Please wait for admin approval."
            )
        
        return data
    
    def save(self):
        """Apply as tutor"""
        user = self.context['request'].user
        profile = user.profile
        
        if not profile.is_tutor:
            profile.is_tutor = True
            from django.utils import timezone
            profile.tutor_application_date = timezone.now()
            profile.save()
        
        return profile

class UserSerializer(serializers.ModelSerializer):
    """Basic user serializer for admin use"""
    profile = UserProfileSerializer(read_only=True)
    
    class Meta:
        model = User
        fields = ('id', 'email', 'first_name', 'last_name', 'profile', 'is_staff')
        read_only_fields = ('id', 'email', 'profile', 'is_staff')