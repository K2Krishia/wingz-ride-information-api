from rest_framework import serializers
from rides.models import User


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for User model for read operations.
    Returns only essential user information (no password or sensitive fields).
    """
    
    class Meta:
        model = User
        fields = ['id_user', 'username', 'first_name', 'last_name', 'email', 'phone_number', 'role']
        read_only_fields = ['id_user']


class UserWriteSerializer(serializers.ModelSerializer):
    """
    Serializer for User model for write operations (create/update).
    Handles password hashing properly.
    """
    password = serializers.CharField(write_only=True, required=False)
    
    class Meta:
        model = User
        fields = ['id_user', 'username', 'first_name', 'last_name', 'email', 'phone_number', 'role', 'password']
        read_only_fields = ['id_user']
    
    def create(self, validated_data):
        """Create user with hashed password"""
        password = validated_data.pop('password', None)
        user = User(**validated_data)
        if password:
            user.set_password(password)
        user.save()
        return user
    
    def update(self, instance, validated_data):
        """Update user, hash password if provided"""
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance
