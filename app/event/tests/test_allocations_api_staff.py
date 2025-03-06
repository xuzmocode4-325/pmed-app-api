from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from event.models import Allocation

from event.serializers import AllocationSerializer

from .helper_for_event_tests import (
    create_user, create_dummy_tray, 
    create_allocation, create_procedures_buffed
)

ALLOCATIONS_URL = reverse('event:allocation-list')

def allocation_detail_url(allocation_id):
    """Create and return a allocation detail url"""
    return reverse('event:allocation-detail', args=[allocation_id])



class StaffAllocationTests(TestCase):
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

        self.client.force_authenticate(self.staff_user)
        self.tray = create_dummy_tray('TT1')

    def test_retrieve_procedures(self):
        """Test retrieving all allocations"""
        t0 = self.tray
        u1, p1 = create_procedures_buffed()
        create_allocation(p1, t0, u1)

        u2, p2 = create_procedures_buffed()
        create_allocation(p2, t0, u2)

        u3, p3 = create_procedures_buffed()
        create_allocation(p3, t0, u3)

        res = self.client.get(ALLOCATIONS_URL)
        allocations = Allocation.objects.all().order_by('-id')

        serializer = AllocationSerializer(allocations, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_allocations_unlimited(self):
        """Test list of allocations"""

        tray = self.tray
        tray1 = create_dummy_tray('TT-1')

        user, procedure = create_procedures_buffed()
        allocation = create_allocation(procedure, tray, user)

        user1, procedure1 = create_procedures_buffed(
            self.staff_user
        )
        allocation1 = create_allocation(procedure1, tray1, user1)

        res = self.client.get(ALLOCATIONS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 2)
        self.assertEqual(res.data[1]['tray'], allocation.tray.id)
        self.assertEqual(res.data[1]['procedure'], allocation.procedure.id)
        self.assertEqual(res.data[0]['tray'], allocation1.tray.id)
        self.assertEqual(res.data[0]['procedure'], allocation1.procedure.id)
    def test_update_allocation(self):
        """Test staff updating an allocation"""

        t0 = self.tray
        t1 = create_dummy_tray('TT-2')      

        u0, p0 = create_procedures_buffed()
        allocation = create_allocation(p0, t0, u0)

        payload = {
            'tray': t1.id
        }

        url = allocation_detail_url(allocation.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        allocation.refresh_from_db()

        self.assertEqual(allocation.tray.id, payload['tray'])
        self.assertEqual(allocation.created_by, u0)
        self.assertEqual(allocation.updated_by, self.staff_user)


    def test_delete_allocation(self):
        """Test staff deleting a user allocation"""









    