"""
Database models.
"""
from django.db import models
from django.db.models import Q
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
        on_delete=models.DO_NOTHING,
        related_name='doctor',
        limit_choices_to=(
            Q(is_staff=False) 
            & ~Q(doctor__isnull=False) 
        )
    )
    practice_number = models.IntegerField(unique=True)
    comments = models.TextField()
    updated = models.DateTimeField(auto_now=True)
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return f"Dr. {self.user.firstname[0]} {self.user.surname} ({self.practice_number})"

    def save(self, *args, **kwargs):
        """Override save method to ensure contact has a hospital."""
        if self.user.firstname is None:
            raise ValidationError("The doctor must be assigned a firstname.")
        if self.user.surname is None:
            raise ValidationError("The doctor must be assigned a surname.")
        if self.practice_number is None:
            raise ValidationError("The doctor must be assigned a practice number.")
        super().save(*args, **kwargs)


    def save(self, *args, **kwargs):
        """Override save method to update the modified_by field."""
        if 'request' in kwargs:
            self.updated_by_by = kwargs.pop('request').user
        super().save(*args, **kwargs)

    
class Product(models.Model):
    TYPE_CHOICES = {
        "Plates": {
            "Plate":"Plate",
            "Titanium Mesh":"Titanium Mesh", 
        },
        "Instruments": {
            "Scissors":"Scissors", 
            "Drill":"Drill", 
            "Screwdriver":"Screwdriver", 
            "Screwdriver Holding Device":"Screwdriver Holding Device",
        },
     
        "Containers":{
            "Container":"Container",
            "Rack":"Rack", 
            "Tray":"Tray"
        },
        "Other":{
            "Screw":"Screw", 
        },
    }

    """Items allocated for each procedure"""
    catalogue_id = models.IntegerField()
    profile = models.DecimalField(max_digits=4, decimal_places=1) 
    item_type = models.TextField(choices=TYPE_CHOICES) # normalize
    description = models.TextField()
    base_price = models.DecimalField(max_digits=8, decimal_places=2)
    vat_price = models.DecimalField(max_digits=8, decimal_places=2)


    def get_digimed(self):
        str_id = str(self.catalogue_id)
        digimed_id = f'{str_id[:2]}-{str_id[2:5]}-{str_id[5:]}'
        return digimed_id

    def __str__(self):
        digimed_id = self.get_digimed()
        return(f"{self.item_type} ({digimed_id})")
    

class TrayType(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()

    class Meta:
        verbose_name_plural = "Tray Types"

    def __str__(self):
        return self.name
    

class TrayItem(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='tray_items'
    )
    quantity = models.PositiveSmallIntegerField()
    tray_type = models.ForeignKey(
        TrayType,
        on_delete=models.CASCADE,
        related_name='tray_items'
    )

    class Meta:
        unique_together = ('tray_type', 'product')

    def __str__(self):
        return f"{self.tray_type.name} - {self.product.item_type} ({self.quantity})"


class Tray(models.Model):
    code = models.CharField(max_length=25, unique=True)
    tray_type = models.ForeignKey(TrayType, on_delete=models.CASCADE, related_name="trays")
    def __str__(self):
        return f"{self.code}: {self.tray_type.name}"
    
  
