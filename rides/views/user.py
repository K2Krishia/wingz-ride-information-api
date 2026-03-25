from rest_framework import viewsets
from rides.models import User
from rides.serializers import UserSerializer, UserWriteSerializer
from rides.permissions import IsAdminUser

class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Users.
    
    Provides full CRUD operations for User model.
    Admin-only access required.
    
    Endpoints:
    - GET /api/users/ - List all users
    - POST /api/users/ - Create new user
    - GET /api/users/{id}/ - Get user details
    - PUT /api/users/{id}/ - Update user
    - PATCH /api/users/{id}/ - Partial update user
    - DELETE /api/users/{id}/ - Delete user
    """
    queryset = User.objects.all()
    permission_classes = [IsAdminUser]
    
    def get_serializer_class(self):
        """Use write serializer for create/update, read serializer for retrieval"""
        if self.action in ['create', 'update', 'partial_update']:
            return UserWriteSerializer
        return UserSerializer
