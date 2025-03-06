"""
Serializers for events APIs
"""
from rest_framework import serializers
from .models import Event, Procedure, Allocation
from core.models import Doctor


class AllocationSerializer(serializers.ModelSerializer):
    """Serializer for allocations"""

    class Meta:
        model = Allocation
        fields = ['id', 'procedure', 'event', 'start_time', 'end_time']
        read_only_fields = ['id', 'created_at', 'updated_at', 'created_by', 'updated_by']


class ProcedureSerializer(serializers.ModelSerializer):
    """Serializer for procedures"""

    class Meta:
        model = Procedure
        fields = ['id', 'patient_name', 'patient_surname',
            'patient_age', 'case_number', 'event', 'description', 
            'ward']
        read_only_fields = [
            'id', 'created_at', 'updated_at', 'created_by', 'updated_by',
        ]


class EventSerializer(serializers.ModelSerializer):
    """Serializer for events"""

    class Meta:
        model = Event
        fields = [
            'id', 'doctor', 'created_at', 'hospital',
            'updated_at', 'created_by', 'updated_by',
        ]
        read_only_fields = [
            'id', 'created_at', 'updated_at', 'created_by', 
            'updated_by',
        ]

    def validate(self, attrs):
        """Ensure that only verified doctors can be associated with events."""
        # Access the authenticated user from the context
        user = self.context['request'].user
        doctor = attrs.get('doctor')

        if self.instance is None:
            if doctor and not doctor.is_verified:
                raise serializers.ValidationError(
                    "The doctor must be verified to be associated with an event."
                )
            if not user.is_staff:
                if doctor != Doctor.objects.get(user=user):
                    raise serializers.ValidationError(
                        "You can only create events for your own profile."
                    )
        else:
            # For updates, use the existing doctor if not provided in attrs
            doctor = attrs.get('doctor', self.instance.doctor)
            if doctor and not doctor.is_verified:
                raise serializers.ValidationError(
                    "The doctor must be verified to be associated with an event."
                )
             # Check if the user is not a staff member
            if not user.is_staff:
            # Check if the doctor field is being updated
                if  doctor != Doctor.objects.get(user=user):
                    raise serializers.ValidationError(
                        "Your profile is not permitted to re-assing events to other doctor."
                    )
                
        return attrs

    def create(self, validated_data):
        """Create a new event and set the created_by field to the authenticated user."""
        user = self.context['request'].user
        validated_data['created_by'] = user

        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        """Update an event and set the updated_by field to the authenticated user."""
        validated_data['updated_by'] = self.context['request'].user

        return super().update(instance, validated_data)
        

class EventDetailSerializer(EventSerializer):
    """Serializer for event detail view"""

    class Meta(EventSerializer.Meta):
        fields = EventSerializer.Meta.fields + ['description']


