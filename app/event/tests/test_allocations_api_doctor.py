from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from event.models import Allocation

from event.serializers import AllocationSerializer

from .helper_for_event_tests import (
    create_event, create_procedure, 
    create_random_entities, generate_random_patient_details, 
    create_dummy_tray, create_allocation
)

ALLOCATIONS_URL = reverse('event:allocation-list')

def allocation_detail_url(allocation_id):
    """Create and return a allocation detail url"""
    return reverse('event:allocation-detail', args=[allocation_id])


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
        self.procedure = create_procedure(
            self.event, 
            **self.patient_details
        )

    def test_retrieve_allocation(self):
        patient1 = generate_random_patient_details()
        procedure1 = create_procedure(
            event=self.event, **patient1
        )
        tray1 = create_dummy_tray('TT-1')
        create_allocation(
            procedure1,
            tray1,
            self.user,
        )

        patient2 = generate_random_patient_details()
        procedure2 = create_procedure(
            event=self.event, **patient2
        )
        tray2 = create_dummy_tray('TT-2')
        create_allocation(
            procedure2,
            tray2,
            self.user,
        )

        patient3 = generate_random_patient_details()
        procedure3 = create_procedure(
            event=self.event, **patient3
        )
        tray3 = create_dummy_tray('TT-3')
        create_allocation(
            procedure3,
            tray3,
            self.user, 
        )

        res = self.client.get(ALLOCATIONS_URL)
        allocations = Allocation.objects.all().order_by('-id')
        serializer = AllocationSerializer(allocations, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)


    def test_allocations_limited_users(self):
        """Test list of allocations is user specific"""

        u1, h1, d1 = create_random_entities()
        event1 = create_event(u1, d1, h1)
        patient_details1 = generate_random_patient_details()
        procedure = create_procedure(event1, **patient_details1)
        tray = create_dummy_tray('TT1')
        create_allocation(
            procedure,
            tray, 
            u1
        )
        
        allocation = create_allocation(
            self.procedure,
            tray,
            self.user
        )

        res = self.client.get(ALLOCATIONS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['tray'], allocation.tray.id)
        self.assertEqual(res.data[0]['id'], allocation.id)

    def test_update_allocation(self):
        """Test update a procedure"""
    
        tray1 = create_dummy_tray('TT-1')
        tray2 = create_dummy_tray('TT-2')

        allocation = create_allocation(
            self.procedure, 
            tray1, 
            self.user
        )

        payload = {
            'tray': tray2.id
        }

        url = allocation_detail_url(allocation.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        allocation.refresh_from_db()
        self.assertEqual(allocation.tray.id, payload['tray'])

    def test_delete_allocation(self):
        tray = create_dummy_tray('TT-1')
        allocation = create_allocation(
            self.procedure,  
            tray, 
            self.user,
        ) 

        url = allocation_detail_url(allocation.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        allocations = Allocation.objects.filter(created_by=self.user)
        self.assertFalse(allocations.exists())




    


