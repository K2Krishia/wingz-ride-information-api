from rest_framework import serializers
from rides.models import RideEvent

class RideEventSerializer(serializers.ModelSerializer):
    """
    Serializer for RideEvent model.
    Simple representation of ride events with timestamp and ride reference.
    """
    # use PrimaryKeyRelatedField to get just the id, not the full ride object
    id_ride = serializers.PrimaryKeyRelatedField(read_only=True)
    
    class Meta:
        model = RideEvent
        fields = ['id_ride_event', 'id_ride', 'description', 'created_at']
        read_only_fields = ['id_ride_event', 'id_ride', 'created_at']
