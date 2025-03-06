# from decimal import Decimal

from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from event.models import Event, Doctor
from event.serializers import (
    EventSerializer,
    EventDetailSerializer
)

from .helper_for_event_tests import (
    create_event, create_random_entities
)

EVENTS_URL = reverse('event:event-list')

def event_detail_url(event_id):
    """Create and return a event detail URL"""
    return reverse('event:event-detail', args=[event_id])


class UnverifiedDoctorEventApiTests(TestCase):
    """Tests for unverified doctor event API access."""

    def setUp(self):
        """Create and authenticate an unverified doctor."""
        self.client = APIClient()
        self.user, self.hospital, self.doctor, = create_random_entities(verified=False)
        self.client.force_authenticate(self.user)

    def test_unverified_doctor_event_returns_error(self):
        """Test that unverified doctors return errors."""
    
        create_event(
            created_by=self.user,
            doctor=self.doctor,
            hospital=self.hospital,
        )

        res = self.client.get(EVENTS_URL)

        # Assert that the status code is 403 FORBIDDEN
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

        # Assert that the response contains the expected error detail
        self.assertEqual(res.data, {'detail': 'You do not have permission to perform this action.'})



class VerifiedDoctorEventApiTests(TestCase):
    """Test authenticated API requests"""

    def setUp(self):
        """Set up the test client and create necessary data."""
        self.client = APIClient()
        self.user, self.hospital, self.doctor = create_random_entities()
        self.client.force_authenticate(user=self.user)

    def test_user_doctor_relationship(self):
        """Test that the authenticated user is a doctor."""
        doctor = Doctor.objects.get(user=self.user)
        self.assertEqual(doctor, self.doctor)

    def test_doctor_retrieve_events(self):
        """Test retrieving a list of events."""
        create_event(
            created_by=self.user,
            doctor=self.doctor,
            hospital=self.hospital, 
        )
        create_event(
            created_by=self.user, 
            doctor=self.doctor, 
            hospital=self.hospital,
        )

        res = self.client.get(EVENTS_URL)

        events = Event.objects.all().order_by('-id')
        serializer = EventSerializer(events, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_event_list_limited_user(self):
        """Test list of events is limited to authenticated user"""
        # Create the hospital instance first
        u1, h1, d1 = create_random_entities()

        create_event(
            created_by=u1,
            doctor=d1, 
            hospital=h1,
        )
        create_event(
            created_by=self.user,
            doctor=self.doctor, 
            hospital=self.hospital,
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
            hospital=self.hospital,
        )

        url = event_detail_url(event.id)
        res = self.client.get(url)

        serializer = EventDetailSerializer(event)
        self.assertEqual(res.data, serializer.data)

    def test_create_event(self):
        """Test creating an event via API"""
        payload = {
            'doctor': int(self.doctor.id),
            'description': '4 procedures',
            'hospital': int(self.hospital.id),
        }

        res = self.client.post(EVENTS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        event = Event.objects.get(id=res.data['id'])
        for k, v in payload.items():
            if k in ['doctor', 'hospital']:
                self.assertEqual(getattr(event, k).id, v)  # Compare Doctor IDs
            else:
                self.assertEqual(getattr(event, k), v)
        self.assertEqual(event.created_by, self.user)

    def test_create_other_doctor_event_returns_error(self):
        """Test that creating an event for another doctor returns an error"""
        u1, h1, d1 = create_random_entities()
        payload = {
            'doctor': int(d1.id),
            'description': '4 procedures',
            'hospital': int(h1.id),
        }

        res = self.client.post(EVENTS_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)


    def test_partial_update(self):
        """Test partial update of a event"""
    
        event = create_event(
            created_by=self.user,
            doctor=self.doctor,
            description='Test Event Description',
            hospital=self.hospital,
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
        u1, h1, d1 =  create_random_entities()
        event = create_event(
            created_by=self.user, 
            doctor=self.doctor,
            hospital=self.hospital,
        )

        payload = {'created_by': u1.id}
        url = event_detail_url(event.id)

        self.client.patch(url, payload)
        event.refresh_from_db()

        self.assertEqual(event.created_by, self.user)

    def test_update_doctor_returns_error(self):
        """Test that updating an event's doctor returns an error"""
        u1, h1, d1 = create_random_entities()
        event = create_event(
            created_by=self.user,
            doctor=self.doctor,
            hospital=self.hospital,
        )

        payload = {'doctor': d1.id}
        url = event_detail_url(event.id)

        res = self.client.patch(url, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_other_doctor_event_returns_error(self):
        """Test that updating an event for another doctor returns an error"""
        u1, h1, d1 = create_random_entities()
        event = create_event(
            created_by=u1,
            doctor=d1,
            hospital=h1,
        )

        payload = {'description': 'New description'}
        url = event_detail_url(event.id)

        res = self.client.patch(url, payload)
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_event(self):
        """Test deleting a event successful"""
        event = create_event(created_by=self.user, doctor=self.doctor, hospital=self.hospital)

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
            hospital=h1,
        )

        url = event_detail_url(event.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Event.objects.filter(id=event.id).exists())

