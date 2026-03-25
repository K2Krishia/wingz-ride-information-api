from rest_framework import serializers
from django.utils import timezone
from datetime import timedelta
from rides.models import Ride, RideEvent
from .user import UserSerializer
from .ride_event import RideEventSerializer

class RideSerializer(serializers.ModelSerializer):
    """
    Standard Ride serializer for detail view.
    Includes nested rider and driver information and ALL ride events.
    
    Use this for individual ride retrieval where complete history is needed.
    """
    rider = UserSerializer(source='id_rider', read_only=True)
    driver = UserSerializer(source='id_driver', read_only=True)
    events = RideEventSerializer(many=True, read_only=True)
    
    class Meta:
        model = Ride
        fields = [
            'id_ride', 'status', 'rider', 'driver',
            'pickup_latitude', 'pickup_longitude',
            'dropoff_latitude', 'dropoff_longitude',
            'pickup_time', 'events', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id_ride', 'created_at', 'updated_at']


class RideListSerializer(serializers.ModelSerializer):
    """
    Optimized Ride serializer for list view.
    
    Key Performance Features:
    1. Only includes events from last 24 hours (todays_ride_events)
    2. Uses prefetched data to avoid N+1 queries
    3. Includes optional distance_to_pickup field for distance-based sorting
    
    The ViewSet must use:
    - select_related('id_rider', 'id_driver') for related users
    - Prefetch with filtered queryset for today's events
    """
    rider = UserSerializer(source='id_rider', read_only=True)
    driver = UserSerializer(source='id_driver', read_only=True)
    todays_ride_events = serializers.SerializerMethodField()
    
    # optional field populated by distance annotation in ViewSet
    distance_to_pickup = serializers.FloatField(read_only=True, required=False)
    
    class Meta:
        model = Ride
        fields = [
            'id_ride', 'status', 'rider', 'driver',
            'pickup_latitude', 'pickup_longitude',
            'dropoff_latitude', 'dropoff_longitude',
            'pickup_time', 'todays_ride_events',
            'distance_to_pickup', 'created_at'
        ]
        read_only_fields = ['id_ride', 'created_at']
    
    def get_todays_ride_events(self, obj):
        """
        Returns only ride events from the last 24 hours.
        
        Performance Note:
        This method accesses 'todays_events' which is prefetched in the ViewSet
        using Prefetch with a filtered queryset. This avoids N+1 query problems.
        
        If the prefetch is not configured properly, this will fall back to
        querying the database for each ride (bad for performance).
        """
        # try to access prefetched data first (optimal path)
        if hasattr(obj, 'todays_events'):
            return RideEventSerializer(obj.todays_events, many=True).data
        
        # fallback: manual query (should not happen with proper prefetch)
        # this is here for safety but indicates a ViewSet configuration issue, viewset should be fixed to prefetch properly
        cutoff_time = timezone.now() - timedelta(hours=24)
        events = obj.events.filter(created_at__gte=cutoff_time)
        return RideEventSerializer(events, many=True).data
