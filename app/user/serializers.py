"""
Serializers for the user API view.
"""

from django.contrib.auth import (
    get_user_model,
    authenticate
)
from django.utils.translation import gettext as _

from rest_framework import serializers
from rest_framework.authtoken.models import Token


class UserSerializer(serializers.ModelSerializer):
    """Serializer for the user object, handling serialization and deserialization of user data."""

    class Meta:
        model = get_user_model()
        fields = ['email', 'password', 'name']
        extra_kwargs = {'password': {
            'write_only': True,
            'min_length': 5
        }}
        """Meta class to specify the model to be serialized and additional options.
        
        Attributes:
            model: The model class to be serialized.
            fields: List of fields to be included in the serialization.
            extra_kwargs: Dictionary of additional keyword arguments for specific fields.
                - 'password': Ensures the password is write-only and has a minimum length of 5.
        """

    def create(self, validated_data:dict):
        """Create and return a user with encrypted password.
        
        Args:
            validated_data (dict): The validated data containing user information.
        
        Returns:
            User: A newly created user instance with an encrypted password.
        """
        return get_user_model().objects.create_user(**validated_data)

    def update(self, instance, validated_data:dict):
        """Update and return an existing user, setting the password correctly if provided.
        
        Args:
            instance (User): The existing user instance to be updated.
            validated_data (dict): The validated data containing updated user information.
        
        Returns:
            User: The updated user instance.
        """
        password = validated_data.pop('password', None)
        user = super().update(instance, validated_data)

        if password:
            user.set_password(password)
            user.save()

        return user


class AuthTokenSerializer(serializers.Serializer):
    """Serializer for the auth user token."""
    email = serializers.EmailField()
    password = serializers.CharField(
        style={'input_type': 'password'},
        trim_whitespace=False,
    )

    def validate(self, attrs):
        """Validate and authenticate the user."""
        email = attrs.get('email')
        password = attrs.get('password')
        user = authenticate(
            request=self.context.get('request'),
            username=email,
            password=password
        )

        if not user:
            msg = _('Unable to authenticate with the provided credentials.')
            raise serializers.ValidationError(msg, code='authorization')

        attrs['user'] = user
        return attrs
