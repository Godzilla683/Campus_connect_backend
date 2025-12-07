from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import UserProfile

# Inline admin for UserProfile
class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'
    fields = ('academic_year', 'is_tutor', 'tutor_approved', 'tutor_application_date', 'date_joined')
    readonly_fields = ('date_joined', 'profile_updated')

# Custom User Admin that includes UserProfile
class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)
    list_display = ('email', 'first_name', 'last_name', 'is_staff', 'is_tutor', 'tutor_approved')
    list_filter = ('is_staff', 'is_active', 'profile__is_tutor', 'profile__tutor_approved', 'profile__academic_year')
    
    # Add custom fields to user list
    def is_tutor(self, obj):
        return obj.profile.is_tutor
    is_tutor.boolean = True
    is_tutor.short_description = 'Is Tutor'
    
    def tutor_approved(self, obj):
        return obj.profile.tutor_approved
    tutor_approved.boolean = True
    tutor_approved.short_description = 'Tutor Approved'

# Register the custom UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

# Optional: Also register UserProfile separately if you want to manage it individually
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user_email', 'academic_year', 'is_tutor', 'tutor_approved', 'tutor_application_date', 'date_joined')
    list_filter = ('is_tutor', 'tutor_approved', 'academic_year')
    search_fields = ('user__email', 'user__first_name', 'user__last_name')
    readonly_fields = ('date_joined', 'profile_updated')
    
    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = 'Email'
    user_email.admin_order_field = 'user__email'