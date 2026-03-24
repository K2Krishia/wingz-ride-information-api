from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    """
    Custom User model extending Django's AbstractUser.
    Adds role field for admin/driver/rider distinction and additional profile fields.
    
    Note: Uses 'id_user' as primary key to match the schema requirements.
    """
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('driver', 'Driver'),
        ('rider', 'Rider'),
    ]
    
    id_user = models.AutoField(primary_key=True)
    role = models.CharField(
        max_length=20, 
        choices=ROLE_CHOICES, 
        default='rider',
        db_index=True
    )
    phone_number = models.CharField(max_length=20, blank=True)
    
    # Note: username, first_name, last_name, email, password, etc. already included from AbstractUser
    
    class Meta:
        db_table = 'user'
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['role']),
        ]
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.email})"
    
    @property
    def is_admin(self):
        """Check if user has admin role"""
        return self.role == 'admin'
