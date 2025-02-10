"""
Django admin customisation
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User

class CustomUserAdmin(BaseUserAdmin):
    """Define the admin pages for users"""
    
    # Fields to display in the user list view
    list_display = ('email', 'name', 'is_active')
    
    # Filters available in the user list view
    list_filter = ('is_active',)
    
    # Fields that can be searched in the user list view
    search_fields = ('email', 'name')
    
    # Default ordering of the user list view
    ordering = ('email',)
    
    # Horizontal filters (not used here)
    filter_horizontal = ()
    
    # Fieldsets for the user detail view
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('name',)}),
        ('Permissions', {'fields': (
            'is_active',
            'is_staff',
            'is_superuser')}),
        ('Important Dates', {'fields': ('last_login',)})
    )
    
    # Fieldsets for adding a new user
    add_fieldsets = ((
        None, {
            'classes': ('wide',),
            'fields': (
                'email',
                'name',
                'password1',
                'password2',
                'is_active',
                'is_staff',
                'is_superuser'
                )
            }
        ),
    )
    
    # Fields that are read-only in the user detail view
    readonly_fields = ['last_login']

    def changelist_view(self, request, extra_context=None):
        """
        Override the changelist view to add custom context data.
        
        Args:
            request: The HTTP request object.
            extra_context: Additional context data for the template.
        
        Returns:
            The rendered changelist view with custom context.
        """
        # Add custom context data if needed
        extra_context = extra_context or {}
        message = "Welcome to the user management panel!"
        extra_context['custom_message'] = message

        return super().changelist_view(request, extra_context=extra_context)

# Register the custom user admin with the User model
admin.site.register(User, CustomUserAdmin)