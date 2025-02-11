from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from django_countries.fields import Country

from core.models import Event, Doctor, Hospital
# from event.serializers import (
#     EventSerializer,
#     EventDetailSerializer
# )

EVENT_URL = reverse('event:event-list')

def event_detail_url(event_id):
    """Create and return a recipe detail URL"""
    return reverse('event:event-detail', args=[event_id])

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

def create_user(hospital, **args): 
    defaults = {
        'firstname':'John',
        'surname':'Doe',
        'email':'john.doe@example.com',
        'phone_number':'+1234567890',
    }
    defaults.update(args)
    contact = get_user_model().objects.create(hospital=hospital, **defaults)
    return contact

def create_doctor(user, **params):
    defaults = {
        'practice_number':123456,
        'comments':'Experienced in cardiology.'
    }
    doctor = Doctor.objects.create(user=user, **defaults)
    return doctor

def create_event(user, doctor, hospital, **params):
    event = Event.objects.create(
        user=user,
        doctor=doctor,
        hospital=hospital
    )
    return event

def create_user(**params):
    """Create and return a new user"""
    return get_user_model().objects.create(**params)

class PublicRecipeAPITests(TestCase):
    """Test unauthenticated API requests"""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test auth is required to call API"""
        res = self.client.get(EVENT_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

class PrivateRecipeAPITests(TestCase):
    """Test authenticated API requests"""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user(
            email = 'john@example.com',
            password = 'testytestpassword124'
        )
        self.client.force_authenticate(self.user)

   