from rest_framework import serializers
from rides.models import User

class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for User model.
    Returns only essential user information (no password or sensitive fields).
    """
    
    class Meta:
        model = User
        fields = ['id_user', 'first_name', 'last_name', 'email', 'phone_number', 'role']
        read_only_fields = ['id_user']
