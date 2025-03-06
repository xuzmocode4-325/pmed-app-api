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
        on_delete=models.DO_NOTHING,
        related_name='events',
    )
    description = models.TextField(null=True, blank=True)
    # Add additional fields for the Event model as needed
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        get_user_model(),
        on_delete=models.DO_NOTHING,
        related_name='modified_events',
        null=True
    )
    objects = EventManager()

    def clean(self):
        """Override clean method to validate hospital field."""
        super().clean()  # Call the parent class's clean method
        if self.hospital is None:
            raise ValidationError("Each event needs to be assigned a hospital.")
        
    def __str__(self):
        id = self.id
        doc_surname = self.doctor.user.surname
        hospital = self.hospital.name
        return f"Event #{id}: Dr. {doc_surname} @{hospital}"


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
        on_delete=models.DO_NOTHING,
        related_name='procedure',
    )
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        get_user_model(), 
        on_delete=models.DO_NOTHING,
        related_name='updated_procedures',
        null=True,
    )

    def __str__(self):
        case_ = self.case_number
        name = self.patient_name[0] 
        surname = self.patient_surname
        return f"Case #{case_}: {name}. {surname}"        


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
        on_delete=models.DO_NOTHING,
        related_name='allocation',
    )
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        get_user_model(), 
        on_delete=models.DO_NOTHING,
        related_name='updated_allocations',
        null=True,
    )

    def __str__(self):
        return f"{self.tray} for {self.procedure}"
    
    def save(self, *args, **kwargs):
        """Override save method to modify the updated_by field."""
        if 'request' in kwargs:
            self.updated_by = kwargs.pop('request').user
        super().save(*args, **kwargs)


class Inventory(models.Model):
    tray = models.ForeignKey(
        Tray,
        on_delete=models.CASCADE,
        related_name='inventory'
    )
    item = models.CharField(max_length=255)
    quantity = models.PositiveSmallIntegerField()
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    created_by = models.ForeignKey(
        get_user_model(), 
        on_delete=models.DO_NOTHING,
        related_name='inventory',
    )
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        get_user_model(), 
        on_delete=models.DO_NOTHING,
        related_name='updated_inventory',
        null=True,
    )

    def __str__(self):
        return f"{self.item} - {self.quantity} in {self.tray}"
    
    def save(self, *args, **kwargs):
        """Override save method to modify the updated_by field."""
        if 'request' in kwargs:
            self.updated_by = kwargs.pop('request').user
        super().save(*args, **kwargs)