from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

class UserProfile(models.Model):
    ACADEMIC_YEAR_CHOICES = [
        ('Year 1', 'Year 1'),
        ('Year 2', 'Year 2'),
        ('Year 3', 'Year 3'),
        ('Year 4', 'Year 4'),
        ('Postgrad', 'Postgraduate'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    academic_year = models.CharField(
        max_length=20, 
        choices=ACADEMIC_YEAR_CHOICES, 
        default='Year 1'
    )
    is_tutor = models.BooleanField(default=False)
    tutor_application_date = models.DateTimeField(null=True, blank=True)
    tutor_approved = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    profile_updated = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.email} - {self.academic_year}"
    
    def apply_as_tutor(self):
        """Apply to become a tutor"""
        if not self.is_tutor:
            self.is_tutor = True
            self.tutor_application_date = timezone.now()
            self.save()
            return True
        return False
    
    def approve_tutor(self):
        """Approve tutor application"""
        if self.is_tutor and not self.tutor_approved:
            self.tutor_approved = True
            self.save()
            return True
        return False
    
    def get_full_name(self):
        """Get user's full name"""
        return f"{self.user.first_name} {self.user.last_name}".strip()
    
    class Meta:
        ordering = ['-date_joined']
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Signal to create user profile when a new user is created"""
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Signal to save user profile when user is saved"""
    if hasattr(instance, 'profile'):
        instance.profile.save()