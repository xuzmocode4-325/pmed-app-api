from decimal import Decimal

from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

EVENTS_URL = reverse('event:event-list')

def event_detail_url(event_id):
    """Create and return a event detail URL"""
    return reverse('event:event-detail', args=[event_id])


class PublicEventAPITests(TestCase):
    """Test unauthenticated API requests"""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test auth is required to call API"""
        res = self.client.get(EVENTS_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)