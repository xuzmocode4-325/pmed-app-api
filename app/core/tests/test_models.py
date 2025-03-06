"""
Module for testing any models within the core app.
"""
from decimal import Decimal
from django.urls import reverse
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.db.utils import IntegrityError

from core.models import (
    Hospital, Doctor, Product, 
    TrayType, TrayItem, Tray,
)

from event.models import (
    Event, Procedure, Allocation
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
    
    def test_doctor_creation_no_practice_error(self):
        """Test that creating a doctor without practice no. raises error."""
        user = get_user_model().objects.create(
            email = 'test@example.com',
            password = 'test@123'
        )
        with self.assertRaises(IntegrityError):
            Doctor.objects.create(
                user=user,
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
            hospital=self.hospital,
        )

        id = event.id
        doc_surname = f'Dr. {event.doctor.user.surname}'
        hospital = event.hospital.name
        event_str = f'Event #{id}: {doc_surname} @{hospital}'

        self.assertIsNotNone(event.created_by)
        self.assertEqual(str(event), event_str)

    def test_create_procedure(self):
        """Test creating a procedure is successful"""
        event = Event.objects.create(
            created_by=self.user,
            doctor=self.doctor,
            hospital=self.hospital,
        )

        name = 'Test'
        surname = 'Patient'
        procedure = Procedure.objects.create(
            created_by=self.user,
            patient_name=name,
            patient_surname=surname,
            patient_age=18,
            case_number='12/344343',
            event=event,
            description='A test procedure',
            ward=1
        )
        case_no = procedure.case_number

        str_test = f'Case #{case_no}: {name[0]}. {surname}'
        self.assertEqual(str(procedure), str_test)

    def test_procedure_event_relationship(self):
        """Test the relationship between a procedure and an event"""
        event = Event.objects.create(
            created_by=self.user,
            doctor=self.doctor,
            hospital=self.hospital,
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

        self.assertEqual(event, procedure.event)

    def test_procedure_created_by_relationship(self):
        """Test the relationship between a procedure and the user who created it"""
        event = Event.objects.create(
            created_by=self.user,
            doctor=self.doctor,
            hospital=self.hospital,
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

        self.assertEqual(self.user, procedure.created_by) 

    def test_create_product(self):
        """Test creating a product is successful"""
        product = Product.objects.create(
            catalogue_id=123456,
            profile=0.1,
            item_type='Plate',
            description='A test product',
            base_price=Decimal('100.00'),
            vat_price=Decimal('115.00'),
        )
        id = str(product.catalogue_id)
        digimed_id = f'{id[:2]}-{id[2:5]}-{id[5:]}'

        product_str = f'{product.item_type} ({digimed_id})'
        self.assertEqual(str(product), product_str)

    def test_create_tray_type(self):
        """Test creating a tray type is successful"""
        tray_type = TrayType.objects.create(
            name='Test Tray Type',
            description='A test tray type',
        )

        self.assertEqual(str(tray_type), tray_type.name)

    def test_create_tray_item(self):        
        """Test creating a tray item is successful"""
        product = Product.objects.create(
            catalogue_id=123456,
            description='A test product',
            profile=0.1,
            item_type='Plate',
            base_price=Decimal('100.00'),
            vat_price=Decimal('115.00'),
        )

        tray_type = TrayType.objects.create(
            name='Test Tray Type',
            description='A test tray type',
        )

        tray_item = TrayItem.objects.create(
            product=product,
            tray_type=tray_type,
            quantity=1,
        )

        self.assertEqual(tray_item.product.id, product.id)
        self.assertEqual(tray_item.tray_type, tray_type)
        self.assertEqual(tray_item.quantity, 1)

    def test_create_tray(self):
        """Test creating a tray is successful"""
        tray_type = TrayType.objects.create(
            name='Test Tray Type',
            description='A test tray type',
        )

        tray = Tray.objects.create(
            code='Test Tray',
            tray_type=tray_type,
        )

        tray_str = f'{tray.code}: {tray.tray_type.name}'

        self.assertEqual(tray.tray_type, tray_type)
        self.assertEqual(str(tray), tray_str)

    def test_create_allocation(self): 
        """Test creating an allocation is successful"""
        event = Event.objects.create(
            created_by=self.user,
            doctor=self.doctor,
            hospital=self.hospital,
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

        tray_type = TrayType.objects.create(
            name='Test Tray Type',
            description='A test tray type',
        )


        tray = Tray.objects.create(
            code='Test Tray',
            tray_type=tray_type,
        )

        allocation = Allocation.objects.create(
            created_by=self.user,
            procedure=procedure,
            tray=tray,
        )

        self.assertEqual(allocation.created_by, self.user)
        self.assertEqual(allocation.procedure, procedure)
        self.assertEqual(allocation.tray, tray)
     