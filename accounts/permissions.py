from rest_framework import permissions

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """
    
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions are only allowed to the owner or admin
        # Check if obj is UserProfile
        if hasattr(obj, 'user'):
            return obj.user == request.user or request.user.is_staff
        
        # If obj is User
        if hasattr(obj, 'profile'):
            return obj == request.user or request.user.is_staff
        
        return False

class IsTutor(permissions.BasePermission):
    """
    Permission to check if user is an approved tutor.
    """
    
    def has_permission(self, request, view):
        return bool(
            request.user and 
            request.user.is_authenticated and
            hasattr(request.user, 'profile') and
            request.user.profile.tutor_approved
        )

class IsNotTutor(permissions.BasePermission):
    """
    Permission to check if user is NOT an approved tutor.
    Useful for preventing tutors from applying again.
    """
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        if not hasattr(request.user, 'profile'):
            return False
        
        return not request.user.profile.tutor_approved

class IsAdminOrSelf(permissions.BasePermission):
    """
    Permission to only allow admin or the user themselves.
    """
    
    def has_object_permission(self, request, view, obj):
        # Admin can do anything
        if request.user and request.user.is_staff:
            return True
        
        # Check if obj is UserProfile
        if hasattr(obj, 'user'):
            return obj.user == request.user
        
        # If obj is User
        return obj == request.user