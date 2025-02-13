"""
Views for the recipe API
"""
from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework import permissions

from core.models import Event
from . import serializers


class IsAuthorized(permissions.BasePermission):
    """Custom permission to allow only verified doctors or staff to create events."""

    def has_permission(self, request, view):
        # Check if the user is authenticated
        if not request.user.is_authenticated:
            return False

        # Check if the user is a doctor and is verified
        if hasattr(request.user, 'doctor') and request.user.doctor.is_verified:
            return True
        
        # Allow staff members
        if request.user.is_staff:
            return True

        return False

class EventViewSet(viewsets.ModelViewSet):
    """View for event API management"""
    serializer_class = serializers.EventDetailSerializer
    queryset = Event.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthorized]

    def get_queryset(self):
        """Retrieve events for authenticated users"""
        if self.request.user.is_staff:
            # If the user is a staff member, return all events
            return self.queryset.order_by('-id')
        # Otherwise, return only the events created by the user
        return self.queryset.filter(created_by=self.request.user).order_by('-id')

    def get_serializer_class(self):
        if self.action == 'list':
            return serializers.EventSerializer

        return self.serializer_class
    
    def perform_create(self, serializer):
        """Create new recipe"""
        serializer.save(created_by=self.request.user)