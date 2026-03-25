from rest_framework import viewsets
from rides.models import RideEvent
from rides.serializers import RideEventSerializer
from rides.permissions import IsAdminUser


class RideEventViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing RideEvents.
    
    Provides full CRUD operations for RideEvent model.
    Admin-only access required.
    
    Endpoints:
    - GET /api/ride-events/ - List all ride events
    - POST /api/ride-events/ - Create new ride event
    - GET /api/ride-events/{id}/ - Get ride event details
    - PUT /api/ride-events/{id}/ - Update ride event
    - PATCH /api/ride-events/{id}/ - Partial update ride event
    - DELETE /api/ride-events/{id}/ - Delete ride event
    
    Query Parameters:
    - id_ride: Filter events by ride ID
    """
    queryset = RideEvent.objects.all().select_related('id_ride')
    serializer_class = RideEventSerializer
    permission_classes = [IsAdminUser]
    filterset_fields = ['id_ride']
    ordering = ['-created_at']
