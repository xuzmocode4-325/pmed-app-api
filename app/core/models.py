"""
Database models.
"""
from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin
)

from phonenumber_field.modelfields import PhoneNumberField
from django_countries.fields import CountryField


class UserManager(BaseUserManager):
    """Class for creating a user manager"""

    def create_user(self, email:str, password:str=None, **extrafields):
        """
        Create, save and return a new user.

        Args:
            email (str): The email address of the user.
            password (str, optional): The password for the user. Defaults to None.
            **extrafields: Additional fields for the user model.

        Raises:
            ValueError: If the email is not provided.

        Returns:
            User: The created user instance.
        """
        if not email:
            raise ValueError(
                'An email address is required for user registration.'
            )
        user = self.model(
            email=self.normalize_email(email),
            **extrafields
        )
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email:str, password:str):
        """
        Create, save and return a new superuser.

        Args:
            email (str): The email address of the superuser.
            password (str): The password for the superuser.

        Returns:
            User: The created superuser instance.
        """
        user = self.create_user(email, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)

        return user
    


class EventManager(models.Manager):
    def create_event(self, user, **kwargs):
        """Create an event with the created_by field set to the user."""
        kwargs['created_by'] = user
        return self.create(**kwargs)



class Hospital(models.Model):
    """Model to store hospital names"""
    name = models.CharField(max_length=255, unique=True)
    street = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    country = CountryField()

    def __str__(self):
        return f"{self.name}, {self.city}, {self.state}, {self.country}"


class User(AbstractBaseUser, PermissionsMixin):
    """Model for custom definition of system user fields"""
    email = models.EmailField(max_length=255, unique=True)
    firstname = models.CharField(max_length=128, null=True, blank=True)
    surname = models.CharField(max_length=128, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    phone_number = PhoneNumberField(null=True, blank=True)
   

    objects = UserManager()

    USERNAME_FIELD = 'email'

    def __str__(self):
        return f"{self.firstname} {self.surname}"

   
class Doctor(models.Model):
    """Model to store doctor information"""
    user = models.OneToOneField(
        get_user_model(), 
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='doctor'
    )
    hospital = models.ForeignKey(
        Hospital,
        on_delete=models.SET_NULL,
        related_name='doctors',
        null=True,  # Allow the hospital field to be nullable
        blank=True  # Allow the hospital field to be optional in forms
    )
    practice_number = models.IntegerField(unique=True)
    comments = models.TextField()
    updated = models.DateTimeField(auto_now=True)
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return f"Dr. {self.user.firstname[0]}. {self.user.surname} - {self.practice_number}"

    def save(self, *args, **kwargs):
        """Override save method to ensure contact has a hospital."""
        if self.hospital is None:
            raise ValidationError("The doctor must be associated with a hospital.")
        if self.user.firstname is None:
            raise ValidationError("The doctor must be assigned a firstname.")
        if self.user.surname is None:
            raise ValidationError("The doctor must be assigned a surname.")
        if self.practice_number is None:
            raise ValidationError("The doctor must be assigned a practice number.")
        super().save(*args, **kwargs)


class Event(models.Model):
    """Model to store all events"""
    created_by = models.ForeignKey(
        get_user_model(),
        on_delete=models.DO_NOTHING,  # Change this line
        related_name='event',
    )
    doctor = models.ForeignKey(
        'Doctor',
        on_delete=models.CASCADE,
        related_name='event'
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

    def save(self, *args, **kwargs):
        """Override save method to update the modified_by field."""
        if 'request' in kwargs:
            self.modified_by = kwargs.pop('request').user
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Event {self.id} (Dr. {self.doctor.user.surname})"

class Procedure(models.Model):
    """Tag for filtering recipes"""
    patient_name = models.CharField(max_length=255)
    patient_surname = models.CharField(max_length=255)
    patient_age = models.PositiveSmallIntegerField()
    case_number = models.CharField(max_length=64, unique=True)
    event = models.ForeignKey(
        'Event',
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
        related_name='moified_procedures',
    )

    def __str__(self):
        return f"Case {self.case_number} - for {self.patient_name[0]}. {self.patient_surname}"