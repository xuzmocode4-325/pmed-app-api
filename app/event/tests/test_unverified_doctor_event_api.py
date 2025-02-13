from decimal import Decimal

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


class UnverifiedDoctorEventApiTests(TestCase):
    """Tests for unverified doctor event API access."""

    def setUp(self):
        """Create and authenticate an unverified doctor."""
        self.client = APIClient()

        self.hospital = create_hospital()

        self.user = create_user(**{
            'firstname': 'John',
            'surname': 'Doe',
            'email': 'john.doe@example.com',
            'phone_number': '+1234567890',
        })
        self.doctor = create_doctor(
            user=self.user, 
            hospital=self.hospital,                         
            **{
            'practice_number': 4599067,
            'comments': 'Experienced in cardiology.',
            'is_verified': False
        })
        self.client.force_authenticate(self.user)

    def test_unverified_doctor_event_returns_error(self):
        """Test that unverified doctors return errors."""
    
        create_event(
            created_by=self.user,
            doctor=self.doctor,
        )

        res = self.client.get(EVENTS_URL)

        # Assert that the status code is 403 FORBIDDEN
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

        # Assert that the response contains the expected error detail
        self.assertEqual(res.data, {'detail': 'You do not have permission to perform this action.'})

