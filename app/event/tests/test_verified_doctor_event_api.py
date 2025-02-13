# from decimal import Decimal

from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from django_countries.fields import Country

from core.models import Event, Doctor, Hospital
from event.serializers import (
    EventSerializer,
    EventDetailSerializer
)

from .helper_for_event_tests import (
    create_hospital, create_user, create_doctor, create_event
)

EVENTS_URL = reverse('event:event-list')

def event_detail_url(event_id):
    """Create and return a event detail URL"""
    return reverse('event:event-detail', args=[event_id])

class VerifiedDoctorEventApiTests(TestCase):
    """Test authenticated API requests"""

    def setUp(self):
        """Set up the test client and create necessary data."""
        self.client = APIClient()
        self.hospital = create_hospital()
        self.user = create_user(**{
            'firstname':'John',
            'surname':'Doe',
            'email':'john.doe@example.com',
            'phone_number':'+1234567890',
        })
        self.doctor = create_doctor(
            user=self.user, 
            hospital=self.hospital
        )
        self.client.force_authenticate(user=self.user)

    def test_doctor_retrieve_events(self):
        """Test retrieving a list of events."""
        create_event(
            created_by=self.user,
            doctor=self.doctor, 
        )
        create_event(
            created_by=self.user, 
            doctor=self.doctor, 
        )

        res = self.client.get(EVENTS_URL)

        events = Event.objects.all().order_by('-id')
        serializer = EventSerializer(events, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_event_list_limited_user(self):
        """Test list of events is limited to authenticated user"""
        other_hospital = create_hospital(
            **{
            'name':'Other Test Hospital',
            'street':'123 Main St',
            'city':'Other Test City',
            'state':'Test State',
            'postal_code':'12345',
            'country':Country('US')
            }
        )
        other_user = create_user(**{
            'firstname':'Jack',
            'surname':'Black',
            'email':'jack.black@example.com',
            'phone_number':'+1234567890',
        })
        other_doctor = create_doctor(
            user=other_user, hospital=other_hospital, 
            **{
            'practice_number': 4599067,
            'comments': 'Experienced in cardiology.',
            'is_verified': True
        })
        create_event(
            created_by=other_user,
            doctor=other_doctor, 
        )
        create_event(
            created_by=self.user,
            doctor=self.doctor, 
        )

        res = self.client.get(EVENTS_URL)

        events = Event.objects.filter(created_by=self.user)
        serializer = EventSerializer(events, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_get_event_detail(self):
        """Test getting event detail"""
        event = create_event(
            created_by=self.user,
            doctor=self.doctor, 
        )

        url = event_detail_url(event.id)
        res = self.client.get(url)

        serializer = EventDetailSerializer(event)
        self.assertEqual(res.data, serializer.data)

    def test_create_recipe(self):
        """Test creating an event via API"""
        payload = {
            'doctor': int(self.doctor.id),
            'description': '4 procedures'
        }

        res = self.client.post(EVENTS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        event = Event.objects.get(id=res.data['id'])
        for k, v in payload.items():
            if k == 'doctor':
                self.assertEqual(getattr(event, k).id, v)  # Compare Doctor IDs
            else:
                self.assertEqual(getattr(event, k), v)
        self.assertEqual(event.created_by, self.user)