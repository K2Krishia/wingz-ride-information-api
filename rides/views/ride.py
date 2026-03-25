from rest_framework import viewsets
from django.db.models import Prefetch, F, FloatField
from django.db.models.functions import ACos, Cos, Sin, Radians, Cast
from django.utils import timezone
from datetime import timedelta
from math import radians, cos

from rides.models import Ride, RideEvent
from rides.serializers import (
    RideSerializer, RideListSerializer, RideWriteSerializer
)
from rides.permissions import IsAdminUser
from rides.filters import RideFilter


class RideViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Rides.
    
    Features:
    - Admin-only access (role='admin' required)
    - Filtering by status and rider email
    - Sorting by pickup_time and distance to pickup location
    - Pagination with customizable page size (default: 10, max: 100)
    - Optimized queries to minimize database hits (2-3 queries total)
    - Returns only today's ride events for performance
    
    Query Parameters:
    - status: Filter by ride status (e.g., 'en-route', 'completed')
    - rider_email: Filter by rider's email address
    - ordering: Sort by fields (use '-' prefix for descending)
        * pickup_time: Sort by pickup time
        * -pickup_time: Sort by pickup time (descending, newest first)
        * distance: Sort by distance to pickup (requires latitude & longitude)
    - latitude: GPS latitude for distance calculation (required with distance sorting)
    - longitude: GPS longitude for distance calculation (required with distance sorting)
    - page: Page number (default: 1)
    - page_size: Items per page (default: 10, max: 100)
    
    Examples:
    - /api/rides/?status=en-route
    - /api/rides/?rider_email=alice@example.com
    - /api/rides/?ordering=-pickup_time
    - /api/rides/?ordering=distance&latitude=37.7749&longitude=-122.4194
    - /api/rides/?status=completed&ordering=-pickup_time&page=2&page_size=20
    """
    permission_classes = [IsAdminUser]
    filterset_class = RideFilter
    
    def get_queryset(self):
        """
        Optimized queryset with select_related and prefetch_related.
        
        Performance optimizations:
        1. select_related for rider and driver (1 query)
        2. prefetch_related for today's events only (1 query)
        3. Distance annotation when GPS coordinates provided
        
        Total queries: 2-3 (including pagination count)
        """
        queryset = Ride.objects.all()
        
        queryset = queryset.select_related('id_rider', 'id_driver') # optimized for related user data (1 query)
      
        cutoff_time = timezone.now() - timedelta(hours=24)
        todays_events = Prefetch(
            'events',
            queryset=RideEvent.objects.filter(created_at__gte=cutoff_time).order_by('-created_at'),
            to_attr='todays_events'
        )
        queryset = queryset.prefetch_related(todays_events) # optimized for today's events (1 query)
        

        latitude = self.request.query_params.get('latitude')
        longitude = self.request.query_params.get('longitude')
        ordering = self.request.query_params.get('ordering', '-pickup_time')
        
        # distance annotation
        if latitude and longitude and 'distance' in ordering:
            try:
                lat = float(latitude)
                lon = float(longitude)
                queryset = self._add_distance_annotation(queryset, lat, lon)
            except (ValueError, TypeError):
                pass
        

        if ordering:
            order_fields = [field.strip() for field in ordering.split(',')]
            
            # map 'distance' to 'distance_to_pickup' (the annotated field name)
            order_fields = [
                'distance_to_pickup' if 'distance' in field 
                else '-distance_to_pickup' if '-distance' in field
                else field
                for field in order_fields
            ]
            
            queryset = queryset.order_by(*order_fields)
        
        return queryset
    
    def _add_distance_annotation(self, queryset, user_lat, user_lon):
        """
        Add distance calculation using Haversine formula.
        
        This implementation uses Django ORM to calculate distance directly in the database.
        For PostgreSQL with large datasets, consider using PostGIS extension for better performance.
        
        Haversine Formula:
        a = sin²(Δφ/2) + cos φ1 ⋅ cos φ2 ⋅ sin²(Δλ/2)
        c = 2 ⋅ atan2(√a, √(1−a))
        d = R ⋅ c
        
        where φ is latitude, λ is longitude, R is earth's radius (6371 km)
        
        Args:
            queryset: Base queryset to annotate
            user_lat: User's latitude
            user_lon: User's longitude
            
        Returns:
            Queryset with distance_to_pickup annotation in kilometers
        """
        # convert user's coordinates to radians for calculation
        lat1_rad = radians(user_lat)
        lon1_rad = radians(user_lon)
        
        # database expressions for pickup coordinates in radians
        lat2_rad = Radians(F('pickup_latitude'))
        lon2_rad = Radians(F('pickup_longitude'))
        
        # calculate differences
        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad
        
        # haversine formula components
        # a = sin²(Δφ/2) + cos φ1 ⋅ cos φ2 ⋅ sin²(Δλ/2)
        a = (
            Sin(dlat / 2) * Sin(dlat / 2) +
            cos(lat1_rad) * Cos(lat2_rad) *
            Sin(dlon / 2) * Sin(dlon / 2)
        )
        
        # c = 2 ⋅ atan2(√a, √(1−a))
        # Simplified: c = 2 ⋅ asin(√a)
        # Note: ACos function works differently, so we use: acos(1 - 2a)
        # This is mathematically equivalent and avoids needing atan2
        
        # For small distances, we can use a simpler approximation:
        # c ≈ 2 * asin(sqrt(a))
        # But since Django doesn't have asin, we use:
        # distance = R * acos(cos(lat1) * cos(lat2) * cos(lon2 - lon1) + sin(lat1) * sin(lat2))
        
        # Direct Haversine using available Django functions
        distance = 6371.0 * (  # Earth radius in kilometers
            2.0 * ACos(
                1.0 - 2.0 * a,
                output_field=FloatField()
            )
        )
        
        return queryset.annotate(
            distance_to_pickup=Cast(distance, FloatField())
        )
    
    def get_serializer_class(self):
        """
        Use different serializers for different actions.
        
        - List view: RideListSerializer (optimized, today's events only)
        - Detail view: RideSerializer (complete, all events)
        - Create/Update: RideWriteSerializer (foreign keys as IDs)
        """
        if self.action == 'list':
            return RideListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return RideWriteSerializer
        return RideSerializer
