# from decimal import Decimal

from django.urls import reverse
from django.test import TestCase

from event.models import Event

from rest_framework import status
from rest_framework.test import APIClient

from event.serializers import (
    EventSerializer,
    EventDetailSerializer
)

from .helper_for_event_tests import (
    create_user, create_event, create_random_entities
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
        self.staff_user = create_user(**{
            'firstname':'John',
            'surname':'Doe',
            'email':'john.doe@example.com',
            'phone_number':'+1234567890',
            'is_staff':True,
        })
        self.client.force_authenticate(user=self.staff_user)

    def test_staff_retrieve_events(self):
        """Test retrieving a list of events."""

        u1, h1, d1 = create_random_entities()
        create_event(
            created_by=self.staff_user,
            doctor=d1, 
            hospital=h1,
        )
        u2, h2, d2 = create_random_entities()
        create_event(
            created_by=self.staff_user, 
            doctor=d2, 
            hospital=h2,
        )
        u3, h3, d3 = create_random_entities()
        create_event(
            created_by=self.staff_user, 
            doctor=d3, 
            hospital=h3,
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
            hospital=h1,
        )
        u2, h2, d2 = create_random_entities()
        create_event(
            created_by=u2, 
            doctor=d2, 
            hospital=h2,
        )
        u3, h3, d3 = create_random_entities()
        create_event(
            created_by=u3, 
            doctor=d3, 
            hospital=h3,
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
        event = create_event(
            created_by=u1,
            doctor=d1, 
            hospital=h1,
        )

        url = event_detail_url(event.id)
        res = self.client.get(url)

        serializer = EventDetailSerializer(event)
        self.assertEqual(res.data, serializer.data)

    def test_create_event(self):
        """Test creating an event via API"""

        u1, h1, d1 = create_random_entities()
     
        
        payload = {
            'doctor': int(d1.id),
            'description': '4 procedures',
            'hospital': int(h1.id),
            'date':'2025-03-27',
        }

        res = self.client.post(EVENTS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        event = Event.objects.get(id=res.data['id'])
        for k, v in payload.items():
            if k in ['doctor', 'hospital']:
                self.assertEqual(getattr(event, k).id, v)  # Compare Doctor IDs
            elif k == "date":
                self.assertEqual(
                    getattr(event, k).strftime('%Y-%m-%d'),
                v) # Compare Date Strings
            else:
                self.assertEqual(getattr(event, k), v)
        self.assertEqual(event.created_by, self.staff_user)


    def test_partial_update(self):
        """Test staff partial update of a user event"""

        u1, h1, d1 = create_random_entities()
    
        event = create_event(
            created_by=u1,
            doctor=d1,
            description='Test Event Description',
            hospital=h1,
        )

        payload = {'description': 'New Event Description'}
        url = event_detail_url(event.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        event.refresh_from_db()
        self.assertEqual(event.description, payload['description'])
        self.assertEqual(event.created_by, u1)
        self.assertEqual(event.updated_by, self.staff_user)

    def test_update_user_returns_error_one(self):
        """Test changing the event user results in an error"""
        u1, h1, d1 = create_random_entities()
        event = create_event(
            created_by=self.staff_user,
            doctor=d1, 
            hospital=h1
        )

        payload = {'created_by': u1.id}
        url = event_detail_url(event.id)

        self.client.patch(url, payload)
        event.refresh_from_db()

        self.assertEqual(event.created_by, self.staff_user)

    def test_update_user_returns_error_two(self):
        """Test changing the event user results in an error"""
        u1, h1, d1 = create_random_entities()
        event = create_event(
            created_by=u1,
            doctor=d1, 
            hospital=h1
        )

        payload = {'created_by': self.staff_user.id}
        url = event_detail_url(event.id)

        self.client.patch(url, payload)
        event.refresh_from_db()

        self.assertEqual(event.created_by, u1)

    def test_staff_delete_own_event(self):
        """Test deleting a event successful"""
        u1, h1, d1 = create_random_entities()
        event = create_event(
            created_by=self.staff_user,
            doctor=d1, 
            hospital=h1,
        )

        url = event_detail_url(event.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Event.objects.filter(id=event.id).exists())

    def test_staff_delete_other_users_event(self):
       # Create the hospital instance first
        u1, h1, d1 = create_random_entities()
                
        event = create_event(
            created_by=u1,
            doctor=d1, 
            hospital=h1
        )

        url = event_detail_url(event.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Event.objects.filter(id=event.id).exists())


class UserGetStaffEventApiTests(TestCase):
    """Test authenticated staff API requests"""

    def setUp(self):
        """Set up the test client and create necessary data."""
        self.client = APIClient()
        self.staff_user = create_user(**{
            'firstname':'John',
            'surname':'Doe',
            'email':'john.doe@example.com',
            'phone_number':'+1234567890',
            'is_staff':True,
        })
        self.user, self.hospital, self.doctor = create_random_entities()
        self.client.force_authenticate(user=self.user)

    def test_doctor_can_access_staff_event(self):
        """Test that a doctor can access staff created event"""

        event = create_event(
            created_by=self.staff_user,
            doctor=self.doctor, 
            hospital=self.hospital,
        )

        url = event_detail_url(event.id)
        res = self.client.get(url)

        serializer = EventDetailSerializer(event)
        self.assertEqual(res.data, serializer.data)



    
