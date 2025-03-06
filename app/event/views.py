"""
Views for the recipe API
"""
from rest_framework import viewsets, mixins
from rest_framework.authentication import TokenAuthentication
from rest_framework import permissions

from .models import Event, Procedure, Allocation
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
            return self.queryset.order_by('-created_at')
        # Otherwise, return only the events created by the user
        return self.queryset.filter(doctor=self.request.user.doctor).order_by('-created_at')

    def get_serializer_class(self):
        if self.action == 'list':
            return serializers.EventSerializer

        return self.serializer_class
    
    def perform_create(self, serializer):
        """Create new recipe"""
        serializer.save(created_by=self.request.user)


class ProcedureViewSet(
    mixins.DestroyModelMixin,
    mixins.UpdateModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet
    ):
    
    serializer_class = serializers.ProcedureSerializer
    queryset = Procedure.objects.all()
    autentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthorized]

    def get_queryset(self):
        """Filter queryset to authenticated user"""
        user = self.request.user
        if user.is_staff:
            # If the user is a staff member, return all events
            return self.queryset.order_by('-created_at')
         # Otherwise, return only the procedures related to events assigned to the doctor's profile
        return self.queryset.filter(
            event__doctor__user=user
        ).order_by('-created_at')
    

class AllocationViewSet(viewsets.ModelViewSet):
    """View for allocation API management"""
    serializer_class = serializers.AllocationSerializer
    queryset = Allocation.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthorized]

    def get_queryset(self):
        """Retrieve allocations for authenticated users"""
        user = self.request.user
        if user.is_staff:
            # If the user is a staff member, return all allocations
            return self.queryset.order_by('-created_at')
        # Otherwise, return only the allocations created by the user
        return self.queryset.filter(
            event__doctor__user=user
        ).order_by('-created_at')
    
    def perform_create(self, serializer):
        """Create new allocation"""
        serializer.save(created_by=self.request.user)
    