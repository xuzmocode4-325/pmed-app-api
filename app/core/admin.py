"""
Django admin customisation
"""
from core.models import (
     User, Hospital, Event, Doctor, 
     Procedure, Equipment, Allocation
)
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin


class CustomUserAdmin(BaseUserAdmin):
    """Define the admin pages for users"""
    
    # Fields to display in the user list view
    list_display = (
        'email', 'firstname', 'surname',
        'is_active', 'is_staff'
    )
    
    # Filters available in the user list view
    list_filter = ('is_active', 'is_staff')
    
    # Fields that can be searched in the user list view
    search_fields = ('email', 'firstname', 'surname')
    
    # Default ordering of the user list view
    ordering = ('surname','firstname', 'email',)
    
    # Horizontal filters (not used here)
    filter_horizontal = ()
    
    # Fieldsets for the user detail view
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('firstname', 'surname', 'phone_number')}),
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
                'firstname',
                'surname',
                'email',
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
       

class HospitalAdmin (admin.ModelAdmin):
    list_display = ('name', 'city', 'country',)  
    search_fields = ('name', 'city', 'country',)  


class EventAdmin (admin.ModelAdmin):
    # Fields to display in the user list view
    list_display = (
        'doctor', 'get_hospital', 'description', 'created_by')
    search_fields = (
        'created_by__firstname', 'created_by__surname', 
        'doctor__user__surname', 'description')
    readonly_fields = [
        'created_by', 'created_at', 'updated_by', 'updated_at']

    def get_hospital(self, obj):
        """Return the first name of the associated user."""
        return obj.doctor.hospital
    get_hospital.short_description = 'Hospital'

    def get_doctor(self, obj):
        """Return the first name of the associated user."""
        return f"Dr {obj.doctor.user.surname}"
    get_doctor.short_description = 'Doctor'

    def save_model(self, request, obj, form, change):
        """Override save_model to set created_by to the current user."""
        if not change or not obj.created_by:
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)


class DoctorAdmin(admin.ModelAdmin):
    list_display = (
        'get_firstname', 'get_surname', 'practice_number', 
        'hospital', 'is_verified')
    
    search_fields = (
        'practice_number', 'hospital__name',
        'user__firstname', 'user__surname',
    )
    
    list_filter = ('is_verified',)
    
    def get_firstname(self, obj):
        """Return the first name of the associated user."""
        return obj.user.firstname
    get_firstname.short_description = 'First Name'  # Optional: Set column header

    def get_surname(self, obj):
        """Return the surname of the associated user."""
        return obj.user.surname
    get_surname.short_description = 'Surname'


class ProcedureAdmin(admin.ModelAdmin):
    list_display = ('patient_name', 'patient_surname', 'case_number' ,'get_doctor')
    readonly_fields = ['created_by', 'created_at', 'updated_by', 'updated_at']

    search_fields = (
        'patient_name', 'patient_surname', 'case_number',
        'event__doctor__user__surname')

    def get_doctor(self, obj):
        """Return the doctor associated with the procedure"""
        initial = obj.event.doctor.user.firstname[0]
        surname = obj.event.doctor.user.surname
        return f"Dr. {initial}. {surname}"
    get_doctor.short_description = 'Owned By'
    
    def save_model(self, request, obj, form, change):
        """Override save_model to set created_by to the current user."""
        if not change or not obj.created_by:
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)


class EquipmentAdmin(admin.ModelAdmin):
    list_display = ('catalogue_id', 'get_digimed', 'profile', 'item_type', 'description')
    search_fields = ('catalogue_id', 'item_type',)

    def get_digimed(self, obj):
        str_id = str(obj.catalogue_id)
        digimed_id = f'{str_id[:2]}-{str_id[2:5]}-{str_id[5:]}'
        return digimed_id
    get_digimed.short_description = 'Digimed ID'
    

class AllocationAdmin(admin.ModelAdmin):
    list_display = ('product', 'quantity', 'procedure', 'is_replenishment', 'get_doctor')
    search_fields = (
        'product__item_type', 'procedure__patient_name',
        'procedure__patient_surname', 'procedure__case_number',
        'procedure__event__doctor__user__surname')

    def get_doctor(self, obj):
        """Return the doctor associated with the procedure"""
        initial = obj.procedure.event.doctor.user.firstname[0]
        surname = obj.procedure.event.doctor.user.surname
        return f"Dr. {initial} {surname}"
    get_doctor.short_description = 'Assigned To'
    

# Register the custom user admin with the User model
admin.site.register(User, CustomUserAdmin)
admin.site.register(Hospital, HospitalAdmin)
admin.site.register(Event, EventAdmin)
admin.site.register(Doctor, DoctorAdmin)
admin.site.register(Procedure, ProcedureAdmin)
admin.site.register(Equipment, EquipmentAdmin)
admin.site.register(Allocation, AllocationAdmin)