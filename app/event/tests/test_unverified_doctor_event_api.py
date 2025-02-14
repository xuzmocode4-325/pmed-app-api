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
        """Test that unverified doctors errors."""
    
        create_event(
            created_by=self.user,
            doctor=self.doctor,
        )

        res = self.client.get(EVENTS_URL)

        # Assert that the status code is 403 FORBIDDEN
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

        # Assert that the response contains the expected error detail
        self.assertEqual(res.data, {'detail': 'You do not have permission to perform this action.'})

