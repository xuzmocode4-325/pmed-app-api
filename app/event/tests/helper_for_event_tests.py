
import random
import string
from decimal import Decimal 
from django.contrib.auth import get_user_model
from core.models import (
    Doctor, Hospital
)
from event.models import (
    Event, Procedure
)

from django_countries.fields import Country


def random_string(length):
    """Generate a random string of fixed length."""
    letters = string.ascii_letters
    return ''.join(random.choice(letters) for i in range(length))
    

def random_number_string(length):
    """Generate a random numeric string of fixed length."""
    numbers = string.digits
    return ''.join(random.choice(numbers) for i in range(length))


def create_hospital(**args):
    defaults = {
        'name':'Test Hospital',
        'street':'123 Main St',
        'city':'Test City',
        'state':'Test State',
        'postal_code':'12345',
        'country':Country('US')
    }
    defaults.update(args)
    hospital = Hospital.objects.create(**defaults)
    return hospital


def create_user(**args): 
    defaults = {
        'firstname':'John',
        'surname':'Doe',
        'email':'john.doe@example.com',
        'phone_number':'+1234567890',
    }
    defaults.update(args)
    contact = get_user_model().objects.create(**defaults)
    return contact


def create_doctor(user, **params):
    defaults = {
        'practice_number':123456,
        'comments':'Experienced in cardiology.',
        'is_verified':True
    }
    defaults.update(params)
    doctor = Doctor.objects.create(user=user, **defaults)
    return doctor


def create_event(created_by, doctor, hospital, **params):
    event = Event.objects.create(
        created_by=created_by,
        doctor=doctor,
        hospital=hospital,
    )
    return event


def create_user(**params):
    """Create and return a new user"""
    return get_user_model().objects.create(**params)


def create_procedure(event, **extra_args):
    patient_details = {
        'patient_name': 'Test',  # Generates a random string of 6 characters
        'patient_surname': 'Patient',  # Generates a random string of 8 characters
        'patient_age': random.randint(0, 120),  # Assuming age range from 0 to 120
        'case_number': random_number_string(10),  # Generates a unique 10-digit number
        'description': random_string(128),  # Generates a random string with a max of 200 characters
        'ward': random.randint(1, 50)  # Assuming ward numbers range from 1 to 50
    }
    patient_details.update(extra_args)
    procedure = Procedure.objects.create(event=event, **extra_args)
    return procedure


def create_random_entities(verified=True):
    """Create a random user, hospital, and doctor."""
    # Generate random data
    random_number = random.randint(1, 1000)
    
    # Create a user
    user = get_user_model().objects.create_user(
        email=f'user{random_number}@example.com',
        password='password123',
        firstname=f'Firstname{random_number}',
        surname=f'Surname{random_number}',
    )
    
    # Create a hospital
    hospital = Hospital.objects.create(
        name=f'Hospital{random_number}',
        street=f'{random_number} Main St',
        city=f'City{random_number}',
        state=f'State{random_number}',
        postal_code=f'{random_number:05}',
        country='US'
    )
    
    # Create a doctor
    doctor = Doctor.objects.create(
        user=user,
        practice_number=random_number,
        comments=f'Comments for doctor {random_number}',
        is_verified=verified, 
    )
    
    return user, hospital, doctor

def generate_random_patient_details():
    """Generate random details for a patient."""
    
    patient_details = {
        'patient_name': random_string(6),  # Generates a random string of 6 characters
        'patient_surname': random_string(8),  # Generates a random string of 8 characters
        'patient_age': random.randint(0, 120),  # Assuming age range from 0 to 120
        'case_number': random_number_string(10),  # Generates a unique 10-digit number
        'description': random_string(128),  # Generates a random string with a max of 200 characters
        'ward': random.randint(1, 50)  # Assuming ward numbers range from 1 to 50
    }
    return patient_details

# def generate_random_equipment():
#     # Randomly select a type and subtype
#     type_category = random.choice(list(Equipment.TYPE_CHOICES.keys()))
#     item_type = random.choice(list(Equipment.TYPE_CHOICES[type_category].values()))

#     # Generate random values for other fields
#     catalogue_id = random.randint(100000, 999999)  # Assuming a 6-digit catalogue ID
#     profile = round(random.uniform(0.1, 9.9), 1)  # Random profile with one decimal place
#     description = f"Random description for {item_type}"
#     base_price = round(Decimal(random.uniform(10.00, 1000.00)), 2)  # Random base price
#     vat_price = round(base_price * Decimal(1.2), 2)  # Assuming VAT is 20%

#     # Create an Equipment instance
#     equipment = Equipment(
#         catalogue_id=catalogue_id,
#         profile=profile,
#         item_type=item_type,
#         description=description,
#         base_price=base_price,
#         vat_price=vat_price
#     )

#     equipment.save()

#     return equipment

