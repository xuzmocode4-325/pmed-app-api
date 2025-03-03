from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from event.models import Procedure

from event.serializers import ProcedureSerializer

from .helper_for_event_tests import (
    create_event, create_user,
    create_procedure, create_random_entities,
    generate_random_patient_details
)

PROCEDURES_URL = reverse('event:procedure-list')

def procedure_detail_url(procedure_id):
    """Create and return a procedure detail url"""
    return reverse('event:procedure-detail', args=[procedure_id])

class StaffProcedureApiTests(TestCase):
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

    def test_retrieve_procedures(self):
        """Test retrieving a list of all procedures"""
        u1, h1, d1 = create_random_entities()
        e1  = create_event(created_by=u1, doctor=d1, hospital=h1)
        patient_details1 = generate_random_patient_details()
        create_procedure(event=e1, **patient_details1)

        u2, h2, d2 = create_random_entities()
        e2 = create_event(u2, d2, h2)
        patient_details2 = generate_random_patient_details()
        create_procedure(event=e2, **patient_details2)

        u3, h3, d3 = create_random_entities()
        e3  = create_event(u3, d3, h3)
        patient_details3 = generate_random_patient_details()
        create_procedure(event=e3, **patient_details3)

        res = self.client.get(PROCEDURES_URL)
        procedures = Procedure.objects.all().order_by('-created_at')
        serializer = ProcedureSerializer(procedures, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_procedures_unlimited(self):
        """Test list of procedures is not limited to staff user"""

        e0 = create_event(self.user, self.doctor, self.hospital)
        patient_details1 = generate_random_patient_details()
        procedure2 = create_procedure(e0, **patient_details1)

        e1 = create_event(self.staff_user, self.doctor, self.hospital)
        patient_details2 = generate_random_patient_details()
        procedure1 = create_procedure(event=e1, **patient_details2)

        res = self.client.get(PROCEDURES_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 2)
        self.assertEqual(res.data[0]['patient_name'], procedure1.patient_name)
        self.assertEqual(res.data[1]['patient_name'], procedure2.patient_name)
        self.assertEqual(res.data[0]['id'], procedure1.id)
        self.assertEqual(res.data[1]['id'], procedure2.id)

    def test_update_procedure(self):
        """Test staff updating a user procedure"""
        
        e0 = create_event(created_by=self.user, doctor=self.doctor, hospital=self.hospital)
        patient_details = generate_random_patient_details()
        procedure = create_procedure(event=e0, **patient_details)
        
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
        """Test staff deleting a user procedure"""
        e0 = create_event(created_by=self.user, doctor=self.doctor, hospital=self.hospital)
        patient_details = generate_random_patient_details()
        procedure = create_procedure(event=e0, **patient_details)
        
        url = procedure_detail_url(procedure.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        procedures = Procedure.objects.filter(created_by=self.user)
        self.assertFalse(procedures.exists())