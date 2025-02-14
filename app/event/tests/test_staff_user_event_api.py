# from decimal import Decimal

import random
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

from django.contrib.auth import get_user_model
from core.models import Hospital, Doctor


from .helper_for_event_tests import (
    create_hospital, create_user, create_event, create_random_entities
)

EVENTS_URL = reverse('event:event-list')

def event_detail_url(event_id):
    """Create and return a event detail URL"""
    return reverse('event:event-detail', args=[event_id])

class StaffUserEventApiTests(TestCase):
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
            'is_staff':True,
        })
        self.client.force_authenticate(user=self.user)

    def test_staff_retrieve_events(self):
        """Test retrieving a list of events."""

        u1, h1, d1 = create_random_entities()
        create_event(
            created_by=self.user,
            doctor=d1, 
        )
        u2, h2, d2 = create_random_entities()
        create_event(
            created_by=self.user, 
            doctor=d2, 
        )
        u3, h3, d3 = create_random_entities()
        create_event(
            created_by=self.user, 
            doctor=d3, 
        )

        res = self.client.get(EVENTS_URL)

        events = Event.objects.all().order_by('-id')
        serializer = EventSerializer(events, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_staff_event_list_unlimited(self):
        """Test list of events is shows all user events for staff"""
        # Create the hospital instance first
        
        u1, h1, d1 = create_random_entities()
        create_event(
            created_by=u1,
            doctor=d1, 
        )
        u2, h2, d2 = create_random_entities()
        create_event(
            created_by=u2, 
            doctor=d2, 
        )
        u3, h3, d3 = create_random_entities()
        create_event(
            created_by=u3, 
            doctor=d3, 
        )

        res = self.client.get(EVENTS_URL)

        events = Event.objects.all().order_by('id')
        serializer = EventSerializer(events, many=True)

        sorted_res_data = sorted(res.data, key=lambda x: x['id'])

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(sorted_res_data, serializer.data)

    def test_get_event_detail(self):
        """Test getting event detail"""
        u1, h1, d1 = create_random_entities()
        create_event(
            created_by=self.user,
            doctor=d1, 
        )
        event = create_event(
            created_by=self.user,
            doctor=d1, 
        )

        url = event_detail_url(event.id)
        res = self.client.get(url)

        serializer = EventDetailSerializer(event)
        self.assertEqual(res.data, serializer.data)

    def test_create_event(self):
        """Test creating an event via API"""

        u1, h1, d1 = create_random_entities()
        create_event(
            created_by=self.user,
            doctor=d1, 
        )
        
        payload = {
            'doctor': int(d1.id),
            'description': '4 procedures'
        }

        res = self.client.post(EVENTS_URL, payload)
        print(res.content)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        event = Event.objects.get(id=res.data['id'])
        for k, v in payload.items():
            if k == 'doctor':
                self.assertEqual(getattr(event, k).id, v)  # Compare Doctor IDs
            else:
                self.assertEqual(getattr(event, k), v)
        self.assertEqual(event.created_by, self.user)


    def test_partial_update(self):
        """Test partial update of a event"""

        u1, h1, d1 = create_random_entities()
        create_event(
            created_by=u1,
            doctor=d1, 
        )
       
        event = create_event(
            created_by=self.user,
            doctor=d1,
            description='Test Event Description',
        )

        payload = {'description': 'New Event Description'}
        url = event_detail_url(event.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        event.refresh_from_db()
        self.assertEqual(event.description, payload['description'])
        self.assertEqual(event.created_by, self.user)
        self.assertEqual(event.updated_by, self.user)

    def test_update_user_returns_error(self):
        """Test changing the event user results in an error"""
        u1, h1, d1 = create_random_entities()
        event = create_event(
            created_by=self.user,
            doctor=d1, 
        )

        payload = {'created_by': u1.id}
        url = event_detail_url(event.id)

        self.client.patch(url, payload)
        event.refresh_from_db()

        self.assertEqual(event.created_by, self.user)

    def test_staff_delete_event(self):
        """Test deleting a event successful"""
        u1, h1, d1 = create_random_entities()
        event = create_event(
            created_by=self.user,
            doctor=d1, 
        )

        event = create_event(created_by=self.user, doctor=d1)

        url = event_detail_url(event.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Event.objects.filter(id=event.id).exists())

    def test_delete_other_users_event_error(self):
       # Create the hospital instance first
        u1, h1, d1 = create_random_entities()
                
        event = create_event(
            created_by=u1,
            doctor=d1, 
        )

        url = event_detail_url(event.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Event.objects.filter(id=event.id).exists())
