import django_filters
from .models import Ride

class RideFilter(django_filters.FilterSet):
    """
    Custom filter for Ride model.
    
    Supports filtering by:
    - status: Exact match on ride status (case-insensitive)
    - rider_email: Exact match on rider's email (case-insensitive)
    """
    status = django_filters.CharFilter(field_name='status', lookup_expr='iexact')
    rider_email = django_filters.CharFilter(field_name='id_rider__email', lookup_expr='iexact')
    
    class Meta:
        model = Ride
        fields = ['status', 'rider_email']
