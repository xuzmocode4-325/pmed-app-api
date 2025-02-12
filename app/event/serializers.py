"""
Serializers for events APIs
"""
from rest_framework import serializers
from core.models import Event


class EventSerializer(serializers.ModelSerializer):
    """Serializer for recipes"""

    class Meta:
        model = Event
        fields = ['id', 'user', 'doctor', 'hospital', 'created_at']
        read_only_fields = ['id', 'created_at', 'upated_at']


class EventDetailSerializer(EventSerializer):
    """Serializer for recipe detail view"""

    class Meta(EventSerializer.Meta):
        fields =  EventSerializer.Meta.fields + ['description'] 