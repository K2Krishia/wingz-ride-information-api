from rest_framework import permissions

class IsAdminUser(permissions.BasePermission):
    """
    Custom permission to only allow users with 'admin' role to access the API.
    
    This checks the custom 'role' field in the User model, not Django's is_staff.
    """
    
    def has_permission(self, request, view):
        """
        Check if the authenticated user has admin role.
        """
        return bool(
            request.user and
            request.user.is_authenticated and
            hasattr(request.user, 'role') and
            request.user.role == 'admin'
        )
    
    message = "You must be an admin to access this resource."
