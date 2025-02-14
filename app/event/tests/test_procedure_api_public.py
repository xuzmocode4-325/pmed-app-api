from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

PROCEDURES_URL = reverse('event:procedure-list')

def procedure_detail_url(procedure_id):
    """Create and return a procedure detail url"""
    return reverse('event:procedure-detail', args=[procedure_id])


class PublicProceduresApiTest(TestCase):
    """Test unauthenticated API requests"""

    def setUP(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test auth is required for retrieving procedures"""
        res = self.client.get(PROCEDURES_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)