from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Ride, RideEvent

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Admin interface for custom User model"""
    list_display = ['username', 'email', 'first_name', 'last_name', 'role', 'is_active']
    list_filter = ['role', 'is_active', 'is_staff']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('role', 'phone_number')}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Additional Info', {'fields': ('role', 'phone_number', 'email')}),
    )

@admin.register(Ride)
class RideAdmin(admin.ModelAdmin):
    """Admin interface for Ride model"""
    list_display = ['id_ride', 'status', 'id_rider', 'id_driver', 'pickup_time', 'created_at']
    list_filter = ['status', 'pickup_time', 'created_at']
    search_fields = ['id_rider__email', 'id_driver__email']
    date_hierarchy = 'pickup_time'
    raw_id_fields = ['id_rider', 'id_driver']

@admin.register(RideEvent)
class RideEventAdmin(admin.ModelAdmin):
    """Admin interface for RideEvent model"""
    list_display = ['id_ride_event', 'id_ride', 'description', 'created_at']
    list_filter = ['created_at']
    search_fields = ['description', 'id_ride__id_ride']
    date_hierarchy = 'created_at'
    raw_id_fields = ['id_ride']

