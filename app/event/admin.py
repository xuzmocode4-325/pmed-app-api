from django.contrib import admin

from event.models import (
    Event, Procedure, Allocation
)

@admin.register(Event)
class EventAdmin (admin.ModelAdmin):
    # Fields to display in the user list view
    list_display = (
        'doctor', 'hospital', 'description', 'created_by')
    search_fields = (
        'created_by__firstname', 'created_by__surname', 
        'doctor__user__surname', 'description', 'hospital__name'
    )
    readonly_fields = [
        'created_by', 'created_at', 'updated_by', 'updated_at'
    ]

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



@admin.register(Procedure)
class ProcedureAdmin(admin.ModelAdmin):
    list_display = (
        'patient_name', 'patient_surname', 'case_number',
        'get_doctor', 'get_hospital'
    )
    list_filter = (
        'event__hospital__name', 
        'event__doctor__user__surname', 
        'created_by'
    )
    search_fields = (
        'patient_name', 'patient_surname', 'case_number',
        'event__doctor__user__surname', 'event__hospital', 
    )
    readonly_fields = [
        'created_by', 'created_at', 'updated_by', 'updated_at'
    ]

    def get_hospital(self, obj):
        """Return the hospital associated with the procedure"""
        if obj.event.hospital is not None:
            return obj.event.hospital.name
        else:   
            return 'No Hospital Assigned'
    get_hospital.short_description = 'Hospital'

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


@admin.register(Allocation)
class AllocationAdmin(admin.ModelAdmin):
    list_display = ('tray', 'created_by')
    search_fields = ('tray__code',)
    list_filter = ('created_by',)
    autocomplete_fields = ['tray']
    ordering = ('-created_at',)  # Newest allocations first