from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.utils import timezone
from .models import UserProfile

@receiver(post_save, sender=User)
def send_welcome_email(sender, instance, created, **kwargs):
    """Send welcome email when user is created"""
    if created:
        # In development, just print to console
        print(f"\n=== WELCOME EMAIL ===\n"
              f"To: {instance.email}\n"
              f"Subject: Welcome to Campus Connect!\n"
              f"Body: Hello {instance.first_name}, welcome to Campus Connect!\n"
              f"Your account has been created successfully.\n")

@receiver(pre_save, sender=UserProfile)
def update_profile_timestamp(sender, instance, **kwargs):
    """Update profile_updated timestamp before saving"""
    if instance.pk:  # Only for updates, not creation
        instance.profile_updated = timezone.now()

@receiver(post_save, sender=UserProfile)
def send_tutor_approval_email(sender, instance, created, **kwargs):
    """Send email when tutor is approved"""
    if not created and instance.tutor_approved:
        user = instance.user
        # In development, print to console
        print(f"\n=== TUTOR APPROVAL EMAIL ===\n"
              f"To: {user.email}\n"
              f"Subject: Your Tutor Application Has Been Approved!\n"
              f"Body: Congratulations {user.first_name}!\n"
              f"Your tutor application has been approved.\n"
              f"You can now receive booking requests from students.\n")