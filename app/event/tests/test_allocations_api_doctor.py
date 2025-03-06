from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from event.models import Allocation

from event.serializers import AllocationSerializer

from .helper_for_event_tests import (
    create_event, create_user,
    create_procedure, create_random_entities,
    generate_random_patient_details
)

ALLOCATIONS_URL = reverse('event:allocation-list')

class AllocationProcedureApiTests(TestCase):
    """Test authenticated API requests"""

    def setUp(self):
        """Set up the test client and create necessary data."""
        self.client = APIClient()
        self.user, self.hospital, self.doctor = create_random_entities()
        self.client.force_authenticate(user=self.user)
        self.event = create_event(
            self.user,
            self.doctor,
            self.hospital
        )
        self.patient_details = generate_random_patient_details()
        self.procedure = create_procedure(event=self.event)


