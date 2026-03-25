from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RideViewSet, UserViewSet, RideEventViewSet

router = DefaultRouter()
router.register(r'rides', RideViewSet, basename='ride')
router.register(r'users', UserViewSet, basename='user')
router.register(r'ride-events', RideEventViewSet, basename='rideevent')

urlpatterns = [
    path('', include(router.urls)),
]
