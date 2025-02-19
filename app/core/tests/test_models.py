"""
Module for testing any models within the core app.
"""
from decimal import Decimal
from django.urls import reverse
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from .. models import (
    Hospital, Doctor, Event, Procedure, Equipment, Allocation
)

from django_countries.fields import Country
from phonenumber_field.modelfields import PhoneNumber


class UserModelTests(TestCase):
    """
    Class for testing models.
    """

    def test_create_user_with_email_success(self):
        """Test for successful creation of user with email address"""
        email = 'test@example.com'
        password = 'test@123'
        user = get_user_model().objects.create_user(
            email,
            password,
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_mormalized(self):
        """Test email normalization for new users."""
        sample_emails = [
            ['test1@EXAMPLE.com', 'test1@example.com'],
            ['Test2@Example.com', 'Test2@example.com'],
            ['TEST3@EXAMPLE.COM', 'TEST3@example.com'],
            ['test4@example.COM', 'test4@example.com'],
            ['Test5@Example.Com', 'Test5@example.com']
        ]

        for email, expected in sample_emails:
            user = get_user_model().objects.create_user(email, 'sample123')
            self.assertEqual(user.email, expected)

    def test_new_user_without_email_raises_error(self):
        """Test creating a new user without an email raises a value error."""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user('', 'test123')

    def test_create_superuser(self):
        """Test creating a superuser"""
        user = get_user_model().objects.create_superuser(
            'test@example.com',
            'test123'
        )

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)


class ModelAdminTests(TestCase):
    """Tests for the Hospital model in the admin interface"""

    def setUp(self):
        """Set up the test client and create a superuser and a hospital instance."""
        self.client = Client()
        self.admin_user = get_user_model().objects.create_superuser(
            email='admin@example.com',
            password='testpass123'
        )
        self.client.force_login(self.admin_user)
        self.hospital = Hospital.objects.create(
            name='Test Hospital',
            street='123 Main St',
            city='Test City',
            state='Test State',
            postal_code='12345',
            country='US'
        )
        self.user = get_user_model().objects.create(
            firstname='John',
            surname='Doe',
            email='john.doe@example.com',
            phone_number='+1234567890',
        )
        self.doctor = Doctor.objects.create(
            user=self.user,
            practice_number=123456,
            comments='Experienced in cardiology.',
            hospital=self.hospital
        )
    def test_hospitals_listed(self):
        """Test that hospitals are listed on the admin page"""
        url = reverse('admin:core_hospital_changelist')
        res = self.client.get(url)

        self.assertContains(res, self.hospital.name)
        self.assertEqual(res.status_code, 200)

    def test_hospital_detail_page(self):
        """Test that the hospital detail page works"""
        url = reverse('admin:core_hospital_change', args=[self.hospital.id])
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)
        self.assertContains(res, self.hospital.name)

    def test_hospital_str(self):
        """Test the string representation of the hospital"""
        expected_str = 'Test Hospital, Test City, Test State, US'
        self.assertEqual(str(self.hospital), expected_str)

    def test_user_creation(self):
        """Test that a user instance is created successfully."""
        self.assertEqual(self.user.firstname, 'John')
        self.assertEqual(self.user.surname, 'Doe')
        self.assertEqual(self.user.email, 'john.doe@example.com')
        self.assertEqual(self.user.phone_number, PhoneNumber.from_string('+1234567890'))

    def test_user_str(self):
        """Test the string representation of the user."""
        expected_str = 'John Doe'
        self.assertEqual(str(self.user), expected_str)

    def test_doctor_creation(self):
        """Test that a doctor instance is created successfully."""
        self.assertEqual(self.doctor.user, self.user)
        self.assertEqual(self.doctor.practice_number, 123456)
        self.assertEqual(self.doctor.comments, 'Experienced in cardiology.')
        self.assertEqual(self.doctor.hospital, self.hospital)
    
    def test_doctor_creation_no_hospital_error(self):
        """Test that a doctor instance is created successfully."""

        with self.assertRaises(ValidationError):
            Doctor.objects.create(
                user=self.user,
                practice_number=123456,
                comments='Experienced in neurology.'
        )

    def test_doctor_user_relationship(self):
        """Test the one-to-one relationship between doctor and user."""
        self.assertEqual(self.user.doctor, self.doctor)


    def test_create_event(self):
        "Test creating an event is successful"
        event = Event.objects.create(
            created_by=self.user,
            doctor=self.doctor,
        )

        self.assertIsNotNone(event.created_by)
        self.assertEqual(str(event), f"Event {event.id} (Dr. {event.doctor.user.surname})")

    def test_create_procedure(self):
        event = Event.objects.create(
            created_by=self.user,
            doctor=self.doctor,
        )

        procedure = Procedure.objects.create(
            created_by=self.user,
            patient_name='Test',
            patient_surname='Test',
            patient_age=18,
            case_number='12/344343',
            event=event,
            description='A test procedure',
            ward=1
        )

        str_test = f'Case {procedure.case_number} - for T. Test'

        self.assertEqual(str(procedure), str_test)


    def test_create_product(self):
        item = Equipment.objects.create(
            catalogue_id = 9252517,
            profile = 1.6,
            item_type = 'plate', 
            description = 'Titan Mircoplate',
            base_price = Decimal('7841.36'),
            vat_price = Decimal('9017.57'),
        )

        str_id = str(item.catalogue_id)
        digimed_id = f'{str_id[:2]}-{str_id[2:5]}-{str_id[5:]}'
      
        str_test = f'{item.item_type} ({digimed_id})'
        self.assertEqual(str(item), str_test)


    def test_create_allocation(self):
        item = Equipment.objects.create(
            catalogue_id = 9252517,
            profile = 1.6,
            item_type = 'Plate',
            description = 'Titan Mircoplate',
            base_price = Decimal('7841.36'),
            vat_price = Decimal('9017.57'),
        )

        event = Event.objects.create(
            created_by=self.user,
            doctor=self.doctor,
        )

        procedure = Procedure.objects.create(
            created_by=self.user,
            patient_name='Test',
            patient_surname='Test',
            patient_age=18,
            case_number='12/344343',
            event=event,
            description='A test procedure',
            ward=1
        )

        allocation = Allocation.objects.create(
            procedure=procedure,
            is_replenishment=False,
            product=item, 
            quantity=2,
        )

        str_test = f'{allocation.quantity} x {allocation.product}'

        self.assertEqual(str(allocation), str_test)
