"""
Module for testing any models within the core app.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model


class ModelTests(TestCase):
    """
    Class for testing models.
    """

    def test_create_user_with_email_success(self):
        """Test for successful creation of user with email address."""
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
        """Test creating a superuser."""
        user = get_user_model().objects.create_superuser(
            'test@example.com',
            'test123'
        )

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)
        print(f"Super user creation test: successful")
