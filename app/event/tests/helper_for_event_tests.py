from django.contrib.auth import get_user_model
from core.models import Event, Doctor, Hospital

from django_countries.fields import Country


def create_hospital(**args):
    defaults = {
        'name':'Test Hospital',
        'street':'123 Main St',
        'city':'Test City',
        'state':'Test State',
        'postal_code':'12345',
        'country':Country('US')
    }
    defaults.update(args)
    hospital = Hospital.objects.create(**defaults)
    return hospital

def create_user(**args): 
    defaults = {
        'firstname':'John',
        'surname':'Doe',
        'email':'john.doe@example.com',
        'phone_number':'+1234567890',
    }
    defaults.update(args)
    contact = get_user_model().objects.create(**defaults)
    return contact

def create_doctor(user, hospital, **params):
    defaults = {
        'practice_number':123456,
        'comments':'Experienced in cardiology.',
        'is_verified':True
    }
    defaults.update(params)
    doctor = Doctor.objects.create(user=user, hospital=hospital, **defaults)
    return doctor

def create_event(created_by, doctor, **params):
    event = Event.objects.create(
        created_by=created_by,
        doctor=doctor,
    )
    return event

def create_user(**params):
    """Create and return a new user"""
    return get_user_model().objects.create(**params)