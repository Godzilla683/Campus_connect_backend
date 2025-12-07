# bookings/models.py
from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator

class Subject(models.Model):
    """Model for academic subjects"""
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=10, unique=True, blank=True, null=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']

class Booking(models.Model):
    """Model for booking a tutor session"""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('no_show', 'No Show'),
    ]
    
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='student_bookings'
    )
    
    tutor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='tutor_bookings'
    )
    
    subject = models.ForeignKey(
        Subject,
        on_delete=models.SET_NULL,
        null=True,
        related_name='bookings'
    )
    
    # Booking details
    topic = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    duration_minutes = models.PositiveIntegerField(
        default=60,
        validators=[MinValueValidator(30), MaxValueValidator(240)]
    )
    
    # Scheduling
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    
    # Location (can be virtual or physical)
    location = models.CharField(max_length=200, blank=True)
    is_virtual = models.BooleanField(default=True)
    meeting_link = models.URLField(max_length=500, blank=True)
    
    # Status and tracking
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    cancelled_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='cancelled_bookings'
    )
    cancellation_reason = models.TextField(blank=True)
    
    # Payment (optional for now)
    hourly_rate = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_paid = models.BooleanField(default=False)
    
    # Feedback
    student_rating = models.PositiveIntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    student_review = models.TextField(blank=True)
    tutor_feedback = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.student.email} - {self.tutor.email} - {self.start_time.strftime('%Y-%m-%d %H:%M')}"
    
    def save(self, *args, **kwargs):
        # Auto-calculate end_time if not provided
        if self.start_time and not self.end_time:
            self.end_time = self.start_time + timezone.timedelta(minutes=self.duration_minutes)
        
        # Auto-calculate total amount
        if not self.total_amount:
            hours = self.duration_minutes / 60
            self.total_amount = self.hourly_rate * hours
        
        super().save(*args, **kwargs)
    
    class Meta:
        ordering = ['-start_time']
        indexes = [
            models.Index(fields=['student', 'status']),
            models.Index(fields=['tutor', 'status']),
            models.Index(fields=['start_time']),
        ]