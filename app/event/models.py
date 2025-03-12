"""Client API models."""
from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError


from core.models import Hospital, Tray, Doctor, Product


class EventFlowManager(models.Manager):
    def create_event(self, user, **kwargs):
        """Create an event with the created_by field set to the user."""
        kwargs['created_by'] = user
        return self.create(**kwargs)


class Event(models.Model):
    """Model to store all events"""
    created_by = models.ForeignKey(
        get_user_model(),
        on_delete=models.DO_NOTHING,  # Change this line
        related_name='event',
    )
    doctor = models.ForeignKey(
        Doctor,
        on_delete=models.DO_NOTHING,
        related_name='event'
    )
    hospital = models.ForeignKey(
        Hospital,
        on_delete=models.DO_NOTHING,
        related_name='events',
    )
    date = models.DateField()
    description = models.TextField(null=True, blank=True)
    # Add additional fields for the Event model as needed
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        get_user_model(),
        on_delete=models.DO_NOTHING,
        related_name='modified_events',
        null=True
    )
    objects = EventFlowManager()

    def clean(self):
        """Override clean method to validate hospital field."""
        super().clean()  # Call the parent class's clean method
        if self.hospital is None:
            raise ValidationError("Each event needs to be assigned a hospital.")
        
    def __str__(self):
        id = self.id
        doc_surname = self.doctor.user.surname
        hospital = self.hospital.name
        return f"Event #{id}: Dr. {doc_surname} @{hospital}"
    
    def save(self, *args, **kwargs):
        """Override save method to modify the updated_by field and handle replenishment."""
        if 'request' in kwargs:
            self.updated_by = kwargs.pop('request').user
        super().save(*args, **kwargs)


class Procedure(models.Model):
    """Procedure covered in each event"""
    patient_name = models.CharField(max_length=255)
    patient_surname = models.CharField(max_length=255)
    patient_age = models.PositiveSmallIntegerField()
    case_number = models.CharField(
        max_length=64, unique=True,
    )
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name='procedure'
    )
    description = models.TextField()
    ward = models.PositiveSmallIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        get_user_model(), 
        on_delete=models.DO_NOTHING,
        related_name='procedure',
    )
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        get_user_model(), 
        on_delete=models.DO_NOTHING,
        related_name='updated_procedures',
        null=True,
    )

    objects = EventFlowManager()

    def __str__(self):
        case_ = self.case_number
        name = self.patient_name[0] 
        surname = self.patient_surname
        return f"Case #{case_}: {name}. {surname}"    

    def save(self, *args, **kwargs):
        """Override save method to modify the updated_by field and handle replenishment."""
        if 'request' in kwargs:
            self.updated_by = kwargs.pop('request').user
        super().save(*args, **kwargs)    


class Allocation(models.Model):
    procedure = models.ForeignKey(
        Procedure,
        on_delete=models.CASCADE,
        related_name='allocations'
    )
    tray = models.ForeignKey(
        Tray, 
        on_delete=models.DO_NOTHING,
        related_name='allocations'
    )
    is_replenishment = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    created_by = models.ForeignKey(
        get_user_model(), 
        on_delete=models.DO_NOTHING,
        related_name='allocation',
    )
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        get_user_model(), 
        on_delete=models.DO_NOTHING,
        related_name='updated_allocations',
        null=True,
    )

    objects = EventFlowManager()

    def __str__(self):
        return f"{self.tray} for {self.procedure}"
    
    def save(self, *args, **kwargs):
        """Override save method to modify the updated_by field and handle replenishment."""
        if 'request' in kwargs:
            self.updated_by = kwargs.pop('request').user
        super().save(*args, **kwargs)
    
        if self.is_replenishment:
            self.replenish_tray()

    def replenish_tray(self):
        """Replenish tray items from inventory."""
        tray_items = Inventory.objects.filter(tray=self.tray)
        for tray_item in tray_items:
            inventory_item = Inventory.objects.filter(item=tray_item.item).first()
            if inventory_item and inventory_item.quantity > 0:
                replenish_quantity = min(inventory_item.quantity, tray_item.quantity)
                tray_item.quantity += replenish_quantity
                inventory_item.quantity -= replenish_quantity
                tray_item.save()
                inventory_item.save()


class Inventory(models.Model):
    tray = models.ForeignKey(
        Tray,
        on_delete=models.CASCADE,
        related_name='inventory',
        null=True
    )
    item = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='inventory_items'
    )
    quantity = models.PositiveSmallIntegerField()
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    created_by = models.ForeignKey(
        get_user_model(), 
        on_delete=models.DO_NOTHING,
        related_name='inventory',
    )
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        get_user_model(), 
        on_delete=models.DO_NOTHING,
        related_name='updated_inventory',
        null=True,
    )

    class Meta:
        verbose_name_plural = "Inventory"

    def __str__(self):
        return f"{self.item} - {self.quantity} in {self.tray}"
    
    objects = EventFlowManager()
    
    def save(self, *args, **kwargs):
        """Override save method to modify the updated_by field."""
        if 'request' in kwargs:
            self.updated_by = kwargs.pop('request').user
        super().save(*args, **kwargs)



class Usage(models.Model):
    """Model to log items used in each allocation"""
    allocation = models.ForeignKey(
        Allocation,
        on_delete=models.CASCADE,
        related_name='usages'
    )
    item = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='usage_items'
    )
    quantity = models.PositiveSmallIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        get_user_model(), 
        on_delete=models.DO_NOTHING,
        related_name='usages',
    )
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        get_user_model(), 
        on_delete=models.DO_NOTHING,
        related_name='updated_usages',
        null=True,
    )

    objects = EventFlowManager()

    def __str__(self):
        return f"{self.quantity} of {self.item} used in {self.allocation}"

    def save(self, *args, **kwargs):
        """Override save method to update tray item quantities and inventory."""
        if 'request' in kwargs:
            self.updated_by = kwargs.pop('request').user
        
        super().save(*args, **kwargs)

        # Update tray item quantities
        tray_inventory = Inventory.objects.filter(tray=self.allocation.tray, item=self.item).first()
        if tray_inventory:
            tray_inventory.quantity -= self.quantity
            tray_inventory.save()

        # Update inventory
        inventory = Inventory.objects.filter(item=self.item).first()
        if inventory:
            inventory.quantity -= self.quantity
            inventory.save()


class Order(models.Model):
    """Model to log new orders"""
    supplier = models.CharField(max_length=255)
    invoice = models.CharField(max_length=255, unique=True)
    order_date = models.DateField()
    delivery_date = models.DateField()
    notes = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        get_user_model(),
        on_delete=models.DO_NOTHING,
        related_name='orders',
    )
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        get_user_model(),
        on_delete=models.DO_NOTHING,
        related_name='updated_orders',
        null=True,
    )

    objects = EventFlowManager()

    def __str__(self):
        return f"Order #{self.invoice} from {self.supplier}"


class OrderItem(models.Model):
    """Model to represent items in an order"""
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items'
    )
    item = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='order_items'
    )
    quantity = models.PositiveSmallIntegerField()

    def __str__(self):
        return f"{self.quantity} of {self.item} in order {self.order.invoice}"

    def save(self, *args, **kwargs):
        """Override save method to update inventory quantities."""
        super().save(*args, **kwargs)

        # Update inventory
        inventory, created = Inventory.objects.get_or_create(
            item=self.item,
            defaults={'quantity': 0}
        )
        inventory.quantity += self.quantity
        inventory.save()