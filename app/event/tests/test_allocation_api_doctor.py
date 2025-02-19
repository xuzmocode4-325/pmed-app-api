from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Allocation
from event.serializers import AllocationSerializer

from .helper_for_event_tests import (
    create_event,
    create_procedure, create_random_entities,
    generate_random_patient_details, generate_random_equipment
)

ALLOCATIONS_URL = reverse('event:allocation-list')

def allocation_detail_url(allocation_id):
    """Create and return a procedure detail url"""
    return reverse('event:allocation-detail', args=[allocation_id])

class DoctorAllocationsApiTest(TestCase):
    """Test unauthenticated API requests"""

    def setUp(self):
        """Set up the test client and create necessary data."""
        self.client = APIClient()
        self.user, self.hospital, self.doctor = create_random_entities()
        self.client.force_authenticate(user=self.user)
        self.event = create_event(
            self.user,
            self.doctor
        )
        self.patient = generate_random_patient_details()
        self.procedure =  create_procedure(event=self.event, **self.patient)
      

    def test_retrieve_allocations(self):
        """Test authorized user can retrieve allocation"""
       
        item1 = generate_random_equipment()
        Allocation.objects.create(
            procedure=self.procedure,
            product=item1,
            quantity=5,
            is_replenishment=False,
        )

        item2 = generate_random_equipment()
        Allocation.objects.create(
            procedure=self.procedure, 
            product=item2,
            quantity=5,
            is_replenishment=False,
        )

        allocations = Allocation.objects.all().order_by('-id')
        serializer = AllocationSerializer(allocations, many=True)


        res = self.client.get(ALLOCATIONS_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_allocations_limited_to_user(self):
        """Test list of allocations is limited to authenticated user"""

        u1, h1, d1 = create_random_entities()
        event1 = create_event(u1, d1)
        patient_details1 = generate_random_patient_details()
        procedure = create_procedure(event1, **patient_details1)

        item = generate_random_equipment()

        Allocation.objects.create(
            procedure=procedure,
            product=item,
            quantity=5,
            is_replenishment=False,
        )

        allocation  = Allocation.objects.create(
            procedure=self.procedure,
            product=item,
            quantity=5,
            is_replenishment=False,
        )

        res = self.client.get(ALLOCATIONS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['id'], allocation.id)
        self.assertEqual(res.data[0]['procedure'], allocation.procedure.id)
        self.assertEqual(res.data[0]['quantity'], allocation.quantity)

    def test_update_allocation(self):
        """Test updating an allocation"""
        allocation  = Allocation.objects.create(
            procedure=self.procedure,
            product=generate_random_equipment(),
            quantity=5,
            is_replenishment=False,
        )

        payload = {'quantity': 2}

        url = allocation_detail_url(allocation.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        allocation.refresh_from_db()
        self.assertEqual(allocation.quantity, payload['quantity'])

    def test_delete_allocation(self):
        """Test deleting an allocations"""

        allocation  = Allocation.objects.create(
            procedure=self.procedure,
            product=generate_random_equipment(),
            quantity=5,
            is_replenishment=False,
        )

        url = allocation_detail_url(allocation.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        allocations = Allocation.objects.filter(procedure=self.procedure)
        self.assertFalse(allocations.exists())

    
