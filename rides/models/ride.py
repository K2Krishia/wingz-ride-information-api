from django.db import models
from django.conf import settings
from .base import TimestampedModel

class Ride(TimestampedModel):
    """
    Ride model representing a ride request with pickup/dropoff locations.
    
    Inherits from TimestampedModel for automatic created_at/updated_at fields.
    
    Includes proper indexing for:
    - Status filtering
    - Pickup time sorting
    - Rider/Driver lookups
    """
    STATUS_CHOICES = [
        ('requested', 'Requested'),
        ('en-route', 'En Route'),
        ('pickup', 'Pickup'),
        ('in-progress', 'In Progress'),
        ('dropoff', 'Dropoff'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    id_ride = models.AutoField(primary_key=True)

    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='requested',
        db_index=True
    )
    
    id_rider = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='rides_as_rider',
        db_column='id_rider'
    )
    id_driver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='rides_as_driver',
        db_column='id_driver'
    )
    
    pickup_latitude = models.FloatField()
    pickup_longitude = models.FloatField()
    dropoff_latitude = models.FloatField()
    dropoff_longitude = models.FloatField()
    
    pickup_time = models.DateTimeField(db_index=True)
    
    class Meta:
        db_table = 'ride'
        ordering = ['-pickup_time']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['pickup_time']),
            models.Index(fields=['id_rider']),
            models.Index(fields=['id_driver']),
            models.Index(fields=['status', 'pickup_time']),
        ]
    
    def __str__(self):
        return f"Ride #{self.id_ride} - {self.status}"
