"""
Django admin customisation
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from core.models import (
    User, Hospital, Doctor, 
    Product, TrayType, TrayItem, Tray
)


@admin.register(User)
class CustomUserAdmin(BaseUserAdmin):
    """Define the admin pages for users"""
    
    # Fields to display in the user list view
    list_display = (
        'email', 'firstname', 'surname',
        'is_active', 'is_staff',
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
        ('Personal info', {'fields': ('firstname', 'surname', 'phone_number', 'image')}),
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
       
@admin.register(Hospital)
class HospitalAdmin (admin.ModelAdmin):
    list_display = ('id', 'name', 'city', 'country',)  
    search_fields = ('name', 'city', 'country',)  


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'get_firstname', 'get_surname', 'practice_number', 'is_verified'
    )
    list_filter = ('is_verified',)
    search_fields = (
        'practice_number', 'user__firstname', 'user__surname',
    )
    
    def get_firstname(self, obj):
        """Return the first name of the associated user."""
        return obj.user.firstname
    get_firstname.short_description = 'First Name'  # Optional: Set column header

    def get_surname(self, obj):
        """Return the surname of the associated user."""
        return obj.user.surname
    get_surname.short_description = 'Surname'


# Inline Admin for TrayTypeProduct (Product & Quantity in TrayType)
class TrayItemInline(admin.TabularInline):  # or admin.StackedInline
    model = TrayItem
    extra = 1  # Allows adding new related products easily
    autocomplete_fields = ['product']
    min_num = 1  # Ensures at least one product is added
    fields = ('product', 'quantity')


# Custom filter for Item Type since choices are nested
class ItemTypeFilter(admin.SimpleListFilter):
    title = _('Item Type')
    parameter_name = 'item_type'

    def lookups(self, request, model_admin):
        """Flattens TYPE_CHOICES for filtering"""
        choices = []
        for category, sub_choices in Product.TYPE_CHOICES.items():
            for key, value in sub_choices.items():
                choices.append((key, f"{category} - {value}"))
        return choices

    def queryset(self, request, queryset):
        """Filter queryset based on selection"""
        if self.value():
            return queryset.filter(item_type=self.value())
        return queryset

# Admin class for Product model
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'catalogue_id', 'get_digimed', 'item_type', 'description', 'base_price', 'vat_price')
    search_fields = ('catalogue_id', 'item_type', 'description')
    list_filter = (ItemTypeFilter,)
    ordering = ('catalogue_id',)
    readonly_fields = ('get_digimed',)  # Ensures Digimed ID is displayed but not editable
    list_per_page = 20  # Pagination for better admin usability

    def get_digimed(self, obj):
        return obj.get_digimed()

    get_digimed.short_description = 'Digimed ID'  # Display name in admin


@admin.register(TrayType)
class TrayTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)
    ordering = ('name',)
    inlines = [TrayItemInline]  # Embeds Product-Quantity table inside TrayType admin

@admin.register(Tray)
class TrayAdmin(admin.ModelAdmin):
    list_display = ('code', 'tray_type')
    search_fields = ('code',)
    list_filter = ('tray_type',)
    autocomplete_fields = ['tray_type']
    ordering = ('code',)
