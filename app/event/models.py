"""Client API models."""
from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError


from core.models import Hospital, Tray, Doctor


class EventManager(models.Manager):
    def create_event(self, user, **kwargs):
        """Create an event with the created_by field set to the user."""
        kwargs['created_by'] = user
        return self.create(**kwargs)


class Event(models.Model):
    """Model to store all events"""
    created_by = models.ForeignKey(
        get_user_model(),
        on_delete=models.DO_NOTHING,  # Change this line
        related_name='event',
    )
    doctor = models.ForeignKey(
        Doctor,
        on_delete=models.DO_NOTHING,
        related_name='event'
    )
    hospital = models.ForeignKey(
        Hospital,
        on_delete=models.SET_NULL,
        related_name='events',
        null=True,  # Allow the hospital field to be nullable
        blank=True  # Allow the hospital field to be optional in forms
    )
    description = models.TextField(null=True, blank=True)
    # Add additional fields for the Event model as needed
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        get_user_model(),
        on_delete=models.DO_NOTHING,
        related_name='modified_events',
        null=True,
        blank=True
    )
    objects = EventManager()

    def clean(self):
        """Override clean method to validate hospital field."""
        super().clean()  # Call the parent class's clean method
        if self.hospital is None:
            raise ValidationError("Each event needs to be assigned a hospital.")
        
    def __str__(self):
        return f"Dr. {self.doctor.user.surname} - {self.hospital.name} (Event {self.id})"


class Procedure(models.Model):
    """Procedure covered in each event"""
    patient_name = models.CharField(max_length=255)
    patient_surname = models.CharField(max_length=255)
    patient_age = models.PositiveSmallIntegerField()
    case_number = models.CharField(
        max_length=64, unique=True,
    )
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name='procedure'
    )
    description = models.TextField()
    ward = models.PositiveSmallIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        get_user_model(), 
        null=True,
        blank=True,
        on_delete=models.DO_NOTHING,
        related_name='procedure',
    )
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        get_user_model(), 
        null=True,
        blank=True,
        on_delete=models.DO_NOTHING,
        related_name='updated_procedures',
    )

    def __str__(self):
        case_ = self.case_number
        patient = self.patient_name[0]
        surname = self.patient_surname
        return f"Case {case_} - for {patient}. {surname}"        


class Allocation(models.Model):
    procedure = models.ForeignKey(
        Procedure,
        on_delete=models.CASCADE,
        related_name='allocations'
    )
    tray = models.ForeignKey(
        Tray, 
        on_delete=models.DO_NOTHING,
        related_name='allocations'
    )
    is_replenishment = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    created_by = models.ForeignKey(
        get_user_model(), 
        null=True,
        blank=True,
        on_delete=models.DO_NOTHING,
        related_name='allocation',
    )
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        get_user_model(), 
        null=True,
        blank=True,
        on_delete=models.DO_NOTHING,
        related_name='updated_allocations',
    )

    def __str__(self):
        return f"{self.tray} for {self.procedure}"
    
    def save(self, *args, **kwargs):
        """Override save method to modify the updated_by field."""
        if 'request' in kwargs:
            self.updated_by = kwargs.pop('request').user
        super().save(*args, **kwargs)
