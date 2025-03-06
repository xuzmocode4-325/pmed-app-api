from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from event.models import Procedure

from event.serializers import ProcedureSerializer

from .helper_for_event_tests import (
    create_event, create_procedure, 
    create_random_entities,
    generate_random_patient_details
)

PROCEDURES_URL = reverse('event:procedure-list')

def procedure_detail_url(procedure_id):
    """Create and return a procedure detail url"""
    return reverse('event:procedure-detail', args=[procedure_id])


class DoctorProcedureApiTests(TestCase):
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

    def test_retrieve_procedures(self):
        """Test retrieving a list of procedures"""
        
        patient_details1 = generate_random_patient_details()
        patient_details2 = generate_random_patient_details()
        patient_details3 = generate_random_patient_details()

        create_procedure(event=self.event, **patient_details1)
        create_procedure(event=self.event, **patient_details2)
        create_procedure(event=self.event, **patient_details3)

        res = self.client.get(PROCEDURES_URL)
        procedures = Procedure.objects.all().order_by('-id')
        serializer = ProcedureSerializer(procedures, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_procedures_limited_to_user(self):
        """Test list of procedures is limited to authenticated user"""

        u1, h1, d1 = create_random_entities()
        event1 = create_event(u1, d1, h1)
        patient_details1 = generate_random_patient_details()
        create_procedure(event1, **patient_details1)

        patient_details2 = generate_random_patient_details()
        procedure = create_procedure(event=self.event, **patient_details2)

        res = self.client.get(PROCEDURES_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['patient_name'], procedure.patient_name)
        self.assertEqual(res.data[0]['id'], procedure.id)

    def test_update_procedure(self):
        """Test updating a procedure"""
        patient_details = generate_random_patient_details()
        procedure = create_procedure(event=self.event, **patient_details)
        
        payload = {
            'patient_name': 'Test',
            'patient_surname': 'Update' 
        }

        url = procedure_detail_url(procedure.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        procedure.refresh_from_db()
        self.assertEqual(procedure.patient_name, payload['patient_name'])
        self.assertEqual(procedure.patient_surname, payload['patient_surname'])

    def test_delete_procedure(self):
        """Test deleting a procedure"""
        patient_details = generate_random_patient_details()
        procedure = create_procedure(event=self.event, **patient_details)
        
        url = procedure_detail_url(procedure.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        procedures = Procedure.objects.filter(created_by=self.user)
        self.assertFalse(procedures.exists())