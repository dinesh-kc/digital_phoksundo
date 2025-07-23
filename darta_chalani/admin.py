# darta_chalani/admin.py
from django.contrib import admin
from .models import Darta, Chalani,Department # Only import Darta and Chalani from here

# IMPORTANT: Import Department and FiscalYear from settings_app.models
from settings_app.models import FiscalYear # Assuming these are defined in settings_app/models.py

# You might have a separate admin.py in settings_app for registering
# Department and FiscalYear. If not, you can register them here if needed:
# admin.site.register(Department)
# admin.site.register(FiscalYear)


@admin.register(Darta)
class DartaAdmin(admin.ModelAdmin):
    list_display = (
        'document_number', 'subject', 'document_date', 'fiscal_year', # fiscal_year is now a ForeignKey
        'sender_receiver_info', 'department', 'document_type',
        'is_confidential', 'created_by', 'created_at'
    )
    list_filter = ('fiscal_year', 'department', 'document_type', 'is_confidential')
    search_fields = ('document_number', 'subject', 'sender_receiver_info', 'remarks')
    date_hierarchy = 'document_date'
    # Use raw_id_fields for ForeignKey fields if you expect many instances
    raw_id_fields = ('created_by', 'fiscal_year', 'department')
    # Removed inlines as Attachment model is no longer used for multiple files

    fieldsets = (
        (None, {
            'fields': (
                'document_number', 'subject', 'document_date', 'fiscal_year',
                'sender_receiver_info', 'department', 'document_type',
                'attachment_file' # Include the direct attachment file field
            )
        }),
        ('Additional Details', {
            'fields': (
                'is_confidential', 'expiry_date', 'followup_date', 'remarks'
            ),
            'classes': ('collapse',), # Makes this section collapsible
        }),
        ('Audit Info', {
            'fields': ('created_by',),
            'classes': ('collapse',),
            'description': 'Automatically filled upon creation.'
        }),
    )

    def save_model(self, request, obj, form, change):
        # Automatically set created_by if it's a new object and not already set
        if not obj.pk: # Only on creation
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(Chalani)
class ChalaniAdmin(admin.ModelAdmin):
    list_display = (
        'document_number', 'subject', 'document_date', 'fiscal_year', # fiscal_year is now a ForeignKey
        'sender_receiver_info', 'department', 'document_type',
        'is_confidential', 'created_by', 'created_at'
    )
    list_filter = ('fiscal_year', 'department', 'document_type', 'is_confidential')
    search_fields = ('document_number', 'subject', 'sender_receiver_info', 'remarks')
    date_hierarchy = 'document_date'
    # Use raw_id_fields for ForeignKey fields if you expect many instances
    raw_id_fields = ('created_by', 'fiscal_year', 'department')
    # Removed inlines

    fieldsets = (
        (None, {
            'fields': (
                'document_number', 'subject', 'document_date', 'fiscal_year',
                'sender_receiver_info', 'department', 'document_type',
                'attachment_file' # Include the direct attachment file field
            )
        }),
        ('Additional Details', {
            'fields': (
                'is_confidential', 'expiry_date', 'followup_date', 'remarks'
            ),
            'classes': ('collapse',),
        }),
        ('Audit Info', {
            'fields': ('created_by',),
            'classes': ('collapse',),
            'description': 'Automatically filled upon creation.'
        }),
    )

    def save_model(self, request, obj, form, change):
        # Automatically set created_by if it's a new object and not already set
        if not obj.pk: # Only on creation
            obj.created_by = request.user
        super().save_model(request, obj, form, change)