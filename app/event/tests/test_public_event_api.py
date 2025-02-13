from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from django_countries.fields import Country

from core.models import Event, Doctor, Hospital
from event.serializers import (
    EventSerializer,
    EventDetailSerializer
)


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


    # def test_create_event_with_new_procedures(self):
    #     """Test creating a event with new procedures"""
    #     payload = {
    #         'title': 'Thai Prawn Curry',
    #         'time_minutes': 30,
    #         'price': Decimal('2.50'),
    #         'procedures': [{'name': 'Thai'}, {'name': 'Dinner'}]
    #     }
    #     res = self.client.post(EVENTS_URL, payload, format='json')
    #     self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    #     events = Event.objects.filter(user=self.user)
    #     self.assertEqual(events.count(), 1)

    #     event = events[0]
    #     self.assertEqual(event.procedures.count(), 2)
    #     for procedure in payload['procedures']:
    #         exists = event.procedures.filter(
    #             name=procedure['name'],
    #             user=self.user
    #         ).exists()
    #         self.assertTrue(exists)

    # def test_create_event_with_existing_procedure(self):
    #     """Test creating a event with existing procedure"""

    #     procedure_indian = Procedure.objects.create(user=self.user, name='Indian') # Add procedure model
    #     payload = {
    #         'title': 'Pongal',
    #         'time_minutes': 60,
    #         'price': Decimal('4.50'),
    #         'procedures': [{'name': 'Indian'}, {'name': 'Breakfast'}]
    #     }
    #     res = self.client.post(EVENTS_URL, payload, format='json')
    #     self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    #     events = Event.objects.filter(user=self.user)
    #     self.assertEqual(events.count(), 1)

    #     event = events[0]
    #     self.assertEqual(event.procedures.count(), 2)

    #     self.assertIn(procedure_indian, event.procedures.all())
    #     for procedure in payload['procedures']:
    #         exists = event.procedures.filter(
    #             name=procedure['name'],
    #             user=self.user
    #         ).exists()
    #         self.assertTrue(exists)

    # def test_create_procedure_on_update(self):
    #     """Test creating procedure when updating a event"""
    #     event = create_event(user=self.user)

    #     payload = {'procedures': [{'name': 'Lunch'}]}
    #     url = event_detail_url(event.id)
    #     res = self.client.patch(url, payload, format='json')

    #     self.assertEqual(res.status_code, status.HTTP_200_OK)
    #     new_procedure = Procedure.objects.get(user=self.user, name='Lunch')
    #     self.assertIn(new_procedure, event.procedures.all())

    # def test_update_event_assign_procedure(self):
    #     """Test assigning an existing procedure when updating a event"""
    #     procedure_breakfast = Procedure.objects.create(user=self.user, name='Breakfast')
    #     event = create_event(user=self.user)
    #     event.procedures.add(procedure_breakfast)

    #     procedure_lunch = Procedure.objects.create(user=self.user, name='Lunch')
    #     payload = {'procedures': [{'name': 'Lunch'}]}

    #     url = event_detail_url(event.id)
    #     res = self.client.patch(url, payload, format='json')

    #     self.assertEqual(res.status_code, status.HTTP_200_OK)
    #     self.assertIn(procedure_lunch, event.procedures.all())
    #     self.assertNotIn(procedure_breakfast, event.procedures.all())

    # def test_clear_event_procedures(self):
    #     """Test clearing a event procedures"""
    #     procedure = Procedure.objects.create(user=self.user, name='Dessert')
    #     event = create_event(user=self.user)
    #     event.procedures.add(procedure)

    #     payload = {'procedures': []}
    #     url = event_detail_url(event.id)
    #     res = self.client.patch(url, payload, format='json')
    #     event.refresh_from_db()
    #     self.assertEqual(res.status_code, status.HTTP_200_OK)
    #     self.assertEqual(event.procedures.count(), 0)
   