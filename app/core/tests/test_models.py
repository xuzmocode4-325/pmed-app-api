"""
Module for testing any models within the core app.
"""
from django.urls import reverse
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from .. models import Hospital, Doctor, Event

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
        print(f"User created with email: successful")

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
        print(f"User emails normalized: successful")

    def test_new_user_without_email_raises_error(self):
        """Test creating a new user without an email raises a value error."""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user('', 'test123')
        print(f"New user with no email raises error: successful")

    def test_create_superuser(self):
        """Test creating a superuser"""
        user = get_user_model().objects.create_superuser(
            'test@example.com',
            'test123'
        )

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)
        print(f"Super user creation test: successful")


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
            hospital=self.hospital
        )
        self.user_without_hospital = get_user_model().objects.create(
            firstname='Jane',
            surname='Doe',
            email='jane.doe@example.com',
            phone_number='+1234567890'
        )
        self.doctor = Doctor.objects.create(
            user=self.user,
            practice_number=123456,
            comments='Experienced in cardiology.'
        )
    def test_hospitals_listed(self):
        """Test that hospitals are listed on the admin page"""
        url = reverse('admin:core_hospital_changelist')
        res = self.client.get(url)

        self.assertContains(res, self.hospital.name)
        self.assertEqual(res.status_code, 200)
        print(f"Test hospital is listed {res.status_code}")

    def test_hospital_detail_page(self):
        """Test that the hospital detail page works"""
        url = reverse('admin:core_hospital_change', args=[self.hospital.id])
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)
        self.assertContains(res, self.hospital.name)
        print(f"Test hospital detail page works {res.status_code}")

    def test_hospital_str(self):
        """Test the string representation of the hospital"""
        expected_str = 'Test Hospital, Test City, Test State, US'
        self.assertEqual(str(self.hospital), expected_str)
        print(f" Expected string matches")

    def test_user_creation(self):
        """Test that a user instance is created successfully."""
        self.assertEqual(self.user.firstname, 'John')
        self.assertEqual(self.user.surname, 'Doe')
        self.assertEqual(self.user.email, 'john.doe@example.com')
        self.assertEqual(self.user.phone_number, PhoneNumber.from_string('+1234567890'))
        self.assertEqual(self.user.hospital, self.hospital)

    def test_user_str(self):
        """Test the string representation of the user."""
        expected_str = 'John Doe'
        self.assertEqual(str(self.user), expected_str)

    def test_user_without_hospital(self):
        """Test creating a user without a hospital."""
        user_without_hospital = get_user_model().objects.create(
            firstname='Jane',
            surname='Smith',
            email='jane.smith@example.com',
            phone_number='+0987654321'
        )
        self.assertIsNone(user_without_hospital.hospital)

    def test_doctor_creation(self):
        """Test that a doctor instance is created successfully."""
        self.assertEqual(self.doctor.user, self.user)
        self.assertEqual(self.doctor.practice_number, 123456)
        self.assertEqual(self.doctor.comments, 'Experienced in cardiology.')
    
    def test_doctor_creation_no_hospital_error(self):
        """Test that a doctor instance is created successfully."""

        with self.assertRaises(ValidationError):
            Doctor.objects.create(
                user=self.user_without_hospital,
                practice_number=123456,
                comments='Experienced in neurology.'
        )

    def test_doctor_user_relationship(self):
        """Test the one-to-one relationship between doctor and user."""
        self.assertEqual(self.user.doctor, self.doctor)


    def test_create_event(self):
        "Test creating an event is successful"
        event = Event.objects.create(
            user=self.admin_user,
            doctor=self.doctor,
            hospital=self.hospital,
        )

        self.assertEqual(str(event), f"Event {event.id} (Dr. {event.doctor.user.surname})")



