from django.db import models
from django.utils import timezone
from .ride import Ride

class RideEvent(models.Model):
    """
    RideEvent model for tracking events during a ride lifecycle.
    
    Uses efficient indexing for time-based queries, particularly for:
    - Fetching events from the last 24 hours
    - Filtering by ride and time
    """
    id_ride_event = models.AutoField(primary_key=True)
    id_ride = models.ForeignKey(
        Ride,
        on_delete=models.CASCADE,
        related_name='events',
        db_column='id_ride'
    )
    description = models.CharField(max_length=255)
    created_at = models.DateTimeField(default=timezone.now, db_index=True)
    
    class Meta:
        db_table = 'ride_event'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['id_ride', 'created_at']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"Event #{self.id_ride_event} - {self.description}"
