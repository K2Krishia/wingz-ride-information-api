from rest_framework import serializers
from rides.models import RideEvent, Ride

class RideEventSerializer(serializers.ModelSerializer):
    """
    Serializer for RideEvent model.
    Simple representation of ride events with timestamp and ride reference.
    """
    # use PrimaryKeyRelatedField to accept ride ID for writes
    id_ride = serializers.PrimaryKeyRelatedField(queryset=Ride.objects.all())
    
    class Meta:
        model = RideEvent
        fields = ['id_ride_event', 'id_ride', 'description', 'created_at']
        read_only_fields = ['id_ride_event', 'created_at']
