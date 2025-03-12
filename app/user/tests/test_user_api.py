"""
Tests for the user API
"""
import os
import tempfile
from PIL import Image
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from event.tests.helper_for_event_tests import (
    create_user,
)

CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')
ME_URL = reverse('user:me')
UPLOAD_IMAGE_URL = reverse('user:upload-image')

def image_upload_url(model, id):
    """Create and return an image upload URL"""
    return reverse(f'{model}:{model}-upload-image', args=[id])


class PublicUserApiTest(TestCase):
    """Test the public features of the user API"""
    def setUp(self):
        """Set up the test client for public API tests."""
        self.client = APIClient()

    def test_create_user_success(self):
        """Test creating a user is successful."""
        payload = {
            'email': 'test@example.com',
            'password': 'testpass123',
            'firstname': 'Test',
            'surname': 'User'
        }

        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertNotIn('password', res.data)

        user = get_user_model().objects.get(email=payload['email'])
        self.assertTrue(user.check_password(payload['password']))

    def test_user_with_email_exists_error(self):
        """Test error returned if user with email exists."""
        payload = {
            'email': 'test@example.com',
            'password': 'testpass123',
            'firstname': 'Test'
        }

        create_user(**payload)
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short_error(self):
        """Test error is returned if password less than 5 chars."""
        payload = {
            'email': 'test2@example.com',
            'password': 'test',
            'firstname': 'Test'
        }

        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

        user_exists = get_user_model().objects.filter(
            email=payload['email']
        ).exists()
        self.assertFalse(user_exists)

    def test_create_token_for_user(self):
        """Test generates token for valid credentials."""
        user = {
            'email': 'test5@example.com',
            'password': 'test-pass123',
            'firstname': 'Test',
            'surname': 'User', 
        }
        
        create_user(**user)

        payload = {
            'email': user['email'],
            'password':  user['password']
        }

        res = self.client.post(TOKEN_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('token', res.data)
        

    def test_create_token_bad_credentials(self):
        """Test error returned for invalid credentials."""
        user_details = {
            'firstname': 'Test Name',
            'email': 'test@example.com',
            'password': 'goodpass'
        }
        create_user(**user_details)

        payload = {
            'email': user_details['email'],
            'password': 'badpass'
        }

        res = self.client.post(TOKEN_URL, payload)
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_blank_password(self):
        """Test error returned for blank password."""
        payload = {
            'email': 'test@example.com',
            'password': ''
        }

        res = self.client.post(TOKEN_URL, payload)
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_user_unauthorized(self):
        """Test authentication is required for users."""
        res = self.client.get(ME_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUserApiTest(TestCase):
    """Test API features that require authentication"""

    def setUp(self):
        """Set test client and auth user for private API tests."""
        self.user = create_user(
            email='test@example.com',
            password='examplepass123',
            firstname='Test',
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_profile_success(self):
        """Test profile retrieval for logged in user."""
        res = self.client.get(ME_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, {
            'firstname': self.user.firstname,
            'surname': self.user.surname,
            'email': self.user.email,
            'phone_number': self.user.phone_number
        })

    def test_post_me_not_allowed(self):
        """Test POST is not allowed for me endpoint."""
        res = self.client.post(ME_URL, {})
        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_user_profile(self):
        """Test profile update for authenticated users."""
        payload = {
            'firstname': 'Updated Name',
            'surname': 'Updated Surname',
            'password': 'Password123'
        }

        res = self.client.patch(ME_URL, payload)
        self.user.refresh_from_db()
        self.assertEqual(self.user.firstname, payload['firstname'])
        self.assertTrue(self.user.check_password(payload['password']))
        self.assertEqual(res.status_code, status.HTTP_200_OK)


class ImageUploadTest(TestCase):
    """Test for the image upload API"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email='user@example.com',
            password='testpass123',
            firstname='Test',
            surname='User'
        )
        self.client.force_authenticate(self.user)

    def tearDown(self):
        self.user.image.delete()

    def test_upload_image_to_user(self):
        """Test uploading an image to user"""
        url = UPLOAD_IMAGE_URL
        with tempfile.NamedTemporaryFile(suffix='.jpg') as ntf:
            img = Image.new('RGB', (10, 10))
            img.save(ntf, format='JPEG')
            ntf.seek(0)
            res = self.client.patch(url, {'image': ntf}, format='multipart')

        self.user.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('image', res.data)
        self.assertTrue(os.path.exists(self.user.image.path))

    def test_upload_image_bad_request(self):
        """Test uploading an invalid image"""
        url = UPLOAD_IMAGE_URL
        res = self.client.patch(url, {'image': 'notimage'}, format='multipart')

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)


