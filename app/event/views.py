"""
Views for the recipe API
"""
from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Event
from . import serializers


class EventViewSet(viewsets.ModelViewSet):
    """View for event API management"""
    serializer_class = serializers.EventDetailSerializer
    queryset = Event.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Retrieve events for authenticated users"""
        if self.request.user.is_staff:
            # If the user is a staff member, return all events
            return self.queryset.order_by('-id')
        # Otherwise, return only the events created by the user
        return self.queryset.filter(user=self.request.user).order_by('-id')
    
    def get_serializer_class(self):
        if self.action == 'list':
            return serializers.EventSerializer
        
        return self.serializer_class

    def perform_create(self, serializer):
        """Create new event"""
        serializer.save(user=self.request.user)
