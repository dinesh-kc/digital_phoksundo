# settings_app/admin.py
from django.contrib import admin
from .models import FiscalYear
from .forms import FiscalYearAdminForm # Import your custom admin form

@admin.register(FiscalYear)
class FiscalYearAdmin(admin.ModelAdmin):
    form = FiscalYearAdminForm # Use your custom form for data entry
    
    # Customize the list view in Django Admin
    list_display = (
        'name', 
        'get_nepali_year_display', # Use the model method for Nepali display
        'start_date_ad', 
        'end_date_ad', 
        'is_active'
    )
    list_filter = ('is_active',)
    search_fields = ('name', 'start_date_ad__year', 'end_date_ad__year') # Allow searching by AD year
    
    # Fields that should be visible when adding/editing
    fields = ('start_date_ad', 'end_date_ad', 'name', 'is_active')

    # Optionally, make 'name' read-only in the admin display (already handled by form)
    # readonly_fields = ('name',) 

    class Media:
        # Django Admin uses its own static files system.
        # We need to include the Nepali datepicker JS here specifically for the Admin.
        # Ensure you have STATIC_URL configured in settings.py.
        # Create a static/admin/js/nepali_datepicker_init.js file.
        js = (
            'https://nepali-datepicker.github.io/nepali-datepicker/js/nepali.datepicker.v3.min.js',
            'admin/js/nepali_datepicker_init.js', # Custom JS for admin page
        )
        css = {
            'all': (
                'https://nepali-datepicker.github.io/nepali-datepicker/css/nepali.datepicker.v3.min.css',
            )
        }