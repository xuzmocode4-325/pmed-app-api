"""
Serializers for events APIs
"""
from rest_framework import serializers
from django.shortcuts import get_object_or_404

from .models import Event, Procedure, Allocation
from core.models import Doctor


class GenericCustomSerializer(serializers.ModelSerializer):
    class Meta:
        read_only_fields = [
            'id', 'created_at', 'updated_at', 'created_by', 'updated_by'
        ]


    def create(self, validated_data):
        """Create a new entry and set the created_by field to the authenticated user."""
        user = self.context['request'].user
        validated_data['created_by'] = user

        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        """Update an entry and set the updated_by field to the authenticated user."""
        validated_data['updated_by'] = self.context['request'].user

        return super().update(instance, validated_data)


class AllocationSerializer(GenericCustomSerializer):
    """Serializer for allocations"""

    class Meta(GenericCustomSerializer.Meta):
        model = Allocation
        fields = [
            'id', 'procedure', 'tray', 'is_replenishment', 
            'created_at', 'updated_at', 'created_by', 'updated_by'
        ]
        


class ProcedureSerializer(GenericCustomSerializer):
    """Serializer for procedures"""

    class Meta(GenericCustomSerializer.Meta):
        model = Procedure
        fields = [
            'id', 'patient_name', 'patient_surname',
            'patient_age', 'case_number', 'event', 'description', 
            'ward', 'created_at', 'updated_at', 'created_by', 'updated_by'
        ]


class EventSerializer(GenericCustomSerializer):
    """Serializer for events"""

    class Meta(GenericCustomSerializer.Meta):
        model = Event
        fields = [
            'id', 'doctor', 'hospital', 'created_at', 
            'updated_at', 'created_by', 'updated_by',
        ]

    def validate(self, attrs):
        """Ensure that only verified doctors can be associated with events, procedures, or allocations."""
        user = self.context['request'].user
        doctor = attrs.get('doctor')

        if doctor and not doctor.is_verified:
            raise serializers.ValidationError(
                "The doctor must be verified to be associated with an event, procedure, or allocation."
            )

        # Inside the validate method
        if not user.is_staff:
            if self.instance is None:  # Creating a new entry
                doctor_instance = get_object_or_404(Doctor, user=user)
                if doctor is None or doctor != doctor_instance:
                    raise serializers.ValidationError(
                        "You can only create entries for your own profile."
                    )
            else:  # Updating an existing entry
                existing_doctor = getattr(self.instance, 'doctor', None)
                if existing_doctor and doctor: 
                    if doctor != existing_doctor:
                        raise serializers.ValidationError(
                            "You are not authorized to perform this action."
                        )

        return attrs
        

class EventDetailSerializer(EventSerializer):
    """Serializer for event detail view"""

    class Meta(EventSerializer.Meta):
        fields = EventSerializer.Meta.fields + ['description']


