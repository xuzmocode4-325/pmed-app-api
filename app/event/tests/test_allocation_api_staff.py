from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Allocation

from event.serializers import AllocationSerializer

from .helper_for_event_tests import (
    create_event, create_user,
    create_procedure, create_random_entities,
    generate_random_patient_details, generate_random_equipment
)

ALLOCATIONS_URL = reverse('event:allocation-list')

def allocation_detail_url(allocation_id):
    """Create and return a procedure detail url"""
    return reverse('event:allocation-detail', args=[allocation_id])

class StaffAllocationsApiTests(TestCase):
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
        self.user, self.hospital, self.doctor = create_random_entities()
        self.client.force_authenticate(user=self.staff_user)
        self.event = create_event(created_by=self.staff_user, doctor=self.doctor)
        self.patient = generate_random_patient_details()
        self.procedure =  create_procedure(event=self.event, **self.patient)

    def test_retrieve_allocations(self):
        item1 = generate_random_equipment()
        Allocation.objects.create(
            procedure=self.procedure,
            product=item1,
            quantity=1,
            is_replenishment=False,
        )
        item2 = generate_random_equipment()
        Allocation.objects.create(
            procedure=self.procedure,
            product=item2,
            quantity=2,
            is_replenishment=False,
        )
        item3 = generate_random_equipment()
        Allocation.objects.create(
            procedure=self.procedure,
            product=item3,
            quantity=3,
            is_replenishment=False,
        )

        res = self.client.get(ALLOCATIONS_URL)

        allocations = Allocation.objects.all().order_by('-id')
        serializer = AllocationSerializer(allocations, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_allocations_unlimited(self):
        item0 = generate_random_equipment()
        a0 = Allocation.objects.create(
            procedure=self.procedure,
            product=item0,
            quantity = 2, 
            is_replenishment=False,
        )

        u1, h1, d1 = create_random_entities()
        e1 = create_event(u1, d1)
        p1 = generate_random_patient_details()
        proc1 = create_procedure(e1, **p1)
        item1 = generate_random_equipment()
        a1 = Allocation.objects.create(
            procedure=proc1,
            product=item1,
            quantity=1,
            is_replenishment=False,
        )

        u2, h2, d2 = create_random_entities()
        e2 = create_event(u2, d2)
        p2 = generate_random_patient_details()
        proc2 = create_procedure(e2, **p2)
        item2 = generate_random_equipment()
        a2 = Allocation.objects.create(
            procedure=proc2,
            product=item2,
            quantity=1,
            is_replenishment=False,
        )

        u3, h3, d3 = create_random_entities()
        e3 = create_event(u3, d3)
        p3 = generate_random_patient_details()
        proc3 = create_procedure(e3, **p3)
        item3 = generate_random_equipment()
        a3 = Allocation.objects.create(
            procedure=proc3,
            product=item3,
            quantity=1,
            is_replenishment=False,
        )

        res = self.client.get(ALLOCATIONS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 4)

        sorted_data = sorted(res.data, key=lambda x: x['id'])

        self.assertEqual(sorted_data[0]['id'], a0.id)
        self.assertEqual(sorted_data[0]['procedure'], a0.procedure.id)
        self.assertEqual(sorted_data[0]['quantity'], a0.quantity)

        self.assertEqual(sorted_data[1]['id'], a1.id)
        self.assertEqual(sorted_data[1]['procedure'], a1.procedure.id)
        self.assertEqual(sorted_data[1]['quantity'], a1.quantity)
        
        self.assertEqual(sorted_data[2]['id'], a2.id)
        self.assertEqual(sorted_data[2]['procedure'], a2.procedure.id)
        self.assertEqual(sorted_data[2]['quantity'], a2.quantity)

        self.assertEqual(sorted_data[3]['id'], a3.id)
        self.assertEqual(sorted_data[3]['procedure'], a3.procedure.id)
        self.assertEqual(sorted_data[3]['quantity'], a3.quantity)

    def test_update_allocation(self):
        u1, h1, d1 = create_random_entities()
        e1 = create_event(u1, d1)
        p1 = generate_random_patient_details()
        proc1 = create_procedure(e1, **p1)
        item1 = generate_random_equipment()
        allocation = Allocation.objects.create(
            procedure=proc1,
            product=item1,
            quantity=1,
            is_replenishment=False,
        )

        payload = {'quantity': 5} 
        url = allocation_detail_url(allocation.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        allocation.refresh_from_db()
        self.assertEqual(allocation.quantity, payload['quantity'])


    def test_delete_allocation(self):
        u1, h1, d1 = create_random_entities()
        e1 = create_event(u1, d1)
        p1 = generate_random_patient_details()
        proc1 = create_procedure(e1, **p1)
        item1 = generate_random_equipment()
        allocation = Allocation.objects.create(
            procedure=proc1,
            product=item1,
            quantity=1,
            is_replenishment=False,
        )

        payload = {'quantity': 5} 
        url = allocation_detail_url(allocation.id)
        res = self.client.delete(url, payload)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        allocations = Allocation.objects.filter(procedure__created_by=u1)
        self.assertFalse(allocations.exists())
