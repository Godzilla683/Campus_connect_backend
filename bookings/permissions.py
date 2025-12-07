from rest_framework import permissions

class IsBookingOwner(permissions.BasePermission):
    """Check if user is owner of booking (student or tutor)"""
    
    def has_object_permission(self, request, view, obj):
        return obj.student == request.user or obj.tutor == request.user

class IsTutorOrAdmin(permissions.BasePermission):
    """Check if user is tutor or admin"""
    
    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            (request.user.is_staff or 
             hasattr(request.user, 'profile') and 
             request.user.profile.tutor_approved)
        )