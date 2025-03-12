from django.contrib import admin

from event.models import (
    Event, Procedure, Allocation,
    Inventory, Usage, Order, OrderItem
)

class BaseAdminClass(admin.ModelAdmin):
        readonly_fields = (
            'created_by', 'updated_by', 'created_at', 'updated_at'
        )

        def save_model(self, request, obj, form, change):
            """Override save_model to set created_by to the current user."""
            if not change or not obj.created_by:
                obj.created_by = request.user
            obj.updated_by = request.user
            super().save_model(request, obj, form, change)

class UsageInline(admin.TabularInline):
    model = Usage
    extra = 1
    readonly_fields = ('created_by', 'updated_by', 'created_at', 'updated_at')

    
@admin.register(Event)
class EventAdmin (BaseAdminClass):
    # Fields to display in the user list view
    list_display = (
        'doctor', 'hospital', 'description', 'created_by', 
        'created_at')
    search_fields = (
        'created_by__firstname', 'created_by__surname', 
        'doctor__user__surname', 'description', 'hospital__name'
    )
   
    def get_doctor(self, obj):
        """Return the first name of the associated user."""
        return f"Dr {obj.doctor.user.surname}"
    get_doctor.short_description = 'Doctor'


@admin.register(Procedure)
class ProcedureAdmin(BaseAdminClass):
    list_display = (
        'patient_name', 'patient_surname', 'case_number',
        'get_doctor', 'get_hospital', 'created_at'
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
    


@admin.register(Allocation)
class AllocationAdmin(BaseAdminClass):
    list_display = ('tray', 'created_by')
    search_fields = ('tray__code',)
    list_filter = ('created_by',)
    autocomplete_fields = ['tray']
    ordering = ('-created_at',)  # Newest allocations first
    inlines = [UsageInline]


@admin.register(Inventory)
class InventoryAdmin(BaseAdminClass):
    list_display = ('item', 'quantity', 'tray', 'created_at', 'created_by', 'updated_at', 'updated_by')
    search_fields = ('item', 'tray__name')
    list_filter = ('tray', 'created_at', 'updated_at')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Usage)
class UsageAdmin(BaseAdminClass):
    list_display = ('item', 'quantity', 'allocation', 'created_at', 'created_by', 'updated_at', 'updated_by')
    search_fields = ('item', 'allocation__procedure__case_number')
    list_filter = ('allocation', 'created_at', 'updated_at')


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1


@admin.register(Order)
class OrderAdmin(BaseAdminClass):
    list_display = ('supplier', 'invoice', 'order_date', 'delivery_date', 'created_at', 'created_by', 'updated_at', 'updated_by')
    search_fields = ('supplier', 'invoice')
    list_filter = ('order_date', 'delivery_date', 'created_at', 'updated_at')
    inlines = [OrderItemInline]

