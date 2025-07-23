# # darta_chalani/context_processors.py
from settings_app.models import FiscalYear

def active_fiscal_year_context(request):
    """
    Adds information about the active fiscal year to the template context.
    """
    active_fiscal_year_exists = FiscalYear.objects.filter(is_active=True).exists()
    return {
        'has_active_fiscal_year': active_fiscal_year_exists,
    }


