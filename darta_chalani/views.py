# darta_chalani/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.db import transaction
from django.contrib import messages
from django.core.exceptions import ValidationError

from .models import Darta, Chalani
from .forms import DartaForm, ChalaniForm

# IMPORTANT: Import your FiscalYear model
from settings_app.models import FiscalYear

# --- Helper function to get the active fiscal year ---
def _get_active_fiscal_year():
    """
    Retrieves the single active fiscal year from the database.
    Raises a ValidationError if no active fiscal year is found.
    """
    active_fiscal_year_obj = FiscalYear.objects.filter(is_active=True).first()
    if not active_fiscal_year_obj:
        raise ValidationError('No active Fiscal Year found. Please set one in settings.')
    return active_fiscal_year_obj

# --- Darta Views ---

@login_required
def darta_list(request):
    """Lists all Darta (incoming) documents filtered by the active fiscal year."""
    try:
        active_fiscal_year_obj = _get_active_fiscal_year()
        dartas = Darta.objects.filter(fiscal_year=active_fiscal_year_obj).order_by('-document_date', '-created_at')
        current_display_fiscal_year_name = active_fiscal_year_obj.name
    except ValidationError as e:
        messages.error(request, f'Configuration Error: {e.message}')
        dartas = Darta.objects.none() # Return empty queryset if no active FY
        current_display_fiscal_year_name = "N/A (Configuration Error)"

    context = {
        'dartas': dartas,
        'title': 'Incoming Documents (Darta)',
        'current_display_fiscal_year_name': current_display_fiscal_year_name, # Pass to template for display
    }
    return render(request, 'darta_chalani/darta_list.html', context)

@login_required
@permission_required('darta_chalani.add_darta', raise_exception=True)
def darta_add(request):
    """Handles adding a new Darta document with a single optional attachment."""
    try:
        active_fiscal_year_obj = _get_active_fiscal_year()
    except ValidationError as e:
        messages.error(request, f'Cannot add Darta: {e.message}')
        return redirect('darta_chalani:darta_list') # Redirect if no active FY

    if request.method == 'POST':
        form = DartaForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                with transaction.atomic():
                    darta = form.save(commit=False)
                    darta.created_by = request.user
                    # Explicitly set the fiscal_year to the active one for the new document
                    darta.fiscal_year = active_fiscal_year_obj
                    darta.save() # Model's save method will now use this fiscal_year for numbering
                messages.success(request, 'Darta document added successfully!')
                return redirect('darta_chalani:darta_detail', pk=darta.pk)
            except ValidationError as e:
                # Catch ValidationErrors from the model's save method (e.g., uniqueness issues)
                messages.error(request, f'Error adding Darta: {e.message}')
            except Exception as e:
                # Catch any other unexpected errors during save
                messages.error(request, f'An unexpected error occurred: {e}')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = DartaForm()

    context = {
        'form': form,
        'title': 'Add New Darta Document',
        'current_fiscal_year_name': active_fiscal_year_obj.name # Pass active fiscal year name to template
    }
    return render(request, 'darta_chalani/darta_form.html', context)

@login_required
def darta_detail(request, pk):
    """Displays details of a specific Darta document and its single attachment."""
    darta = get_object_or_404(Darta, pk=pk)
    context = {
        'darta': darta,
        'title': f'Darta Details: {darta.document_number}'
    }
    return render(request, 'darta_chalani/darta_detail.html', context)

@login_required
@permission_required('darta_chalani.change_darta', raise_exception=True)
def darta_edit(request, pk):
    """Handles editing an existing Darta document and its single attachment."""
    darta = get_object_or_404(Darta, pk=pk)
    try:
        # Still retrieve active FY to display in the form context if needed,
        # but the document's fiscal_year should not be changed on edit.
        active_fiscal_year_obj = _get_active_fiscal_year()
    except ValidationError as e:
        messages.error(request, f'Configuration Error: {e.message}')
        return redirect('darta_chalani:darta_detail', pk=pk) # Or appropriate redirect

    if request.method == 'POST':
        form = DartaForm(request.POST, request.FILES, instance=darta)
        if form.is_valid():
            try:
                with transaction.atomic():
                    # No need to set fiscal_year here for an existing object as it's already set
                    # and should not be changed once a document is associated with a fiscal year.
                    form.save()
                messages.success(request, 'Darta document updated successfully!')
                return redirect('darta_chalani:darta_detail', pk=darta.pk)
            except ValidationError as e:
                messages.error(request, f'Error updating Darta: {e.message}')
            except Exception as e:
                messages.error(request, f'An unexpected error occurred: {e}')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = DartaForm(instance=darta)

    context = {
        'form': form,
        'title': f'Edit Darta: {darta.document_number}',
        'current_fiscal_year_name': active_fiscal_year_obj.name # Pass active fiscal year name to template
    }
    return render(request, 'darta_chalani/darta_form.html', context)

@login_required
@permission_required('darta_chalani.delete_darta', raise_exception=True)
def darta_delete(request, pk):
    """Handles deleting a Darta document."""
    darta = get_object_or_404(Darta, pk=pk)
    if request.method == 'POST':
        try:
            darta.delete()
            messages.success(request, 'Darta document deleted successfully.')
            return redirect('darta_chalani:darta_list')
        except Exception as e:
            messages.error(request, f'Error deleting Darta: {e}')
            return redirect('darta_chalani:darta_detail', pk=darta.pk)
    context = {
        'darta': darta,
        'title': f'Confirm Delete Darta: {darta.document_number}'
    }
    return render(request, 'darta_chalani/darta_confirm_delete.html', context)

# --- Chalani Views ---

@login_required
def chalani_list(request):
    """Lists all Chalani (outgoing) documents filtered by the active fiscal year."""
    try:
        active_fiscal_year_obj = _get_active_fiscal_year()
        chalanis = Chalani.objects.filter(fiscal_year=active_fiscal_year_obj).order_by('-document_date', '-created_at')
        current_display_fiscal_year_name = active_fiscal_year_obj.name
    except ValidationError as e:
        messages.error(request, f'Configuration Error: {e.message}')
        chalanis = Chalani.objects.none() # Return empty queryset if no active FY
        current_display_fiscal_year_name = "N/A (Configuration Error)"

    context = {
        'chalanis': chalanis,
        'title': 'Outgoing Documents (Chalani)',
        'current_display_fiscal_year_name': current_display_fiscal_year_name, # Pass to template for display
    }
    return render(request, 'darta_chalani/chalani_list.html', context)

@login_required
@permission_required('darta_chalani.add_chalani', raise_exception=True)
def chalani_add(request):
    """Handles adding a new Chalani document with a single optional attachment."""
    try:
        active_fiscal_year_obj = _get_active_fiscal_year()
    except ValidationError as e:
        messages.error(request, f'Cannot add Chalani: {e.message}')
        return redirect('darta_chalani:chalani_list')

    if request.method == 'POST':
        form = ChalaniForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                with transaction.atomic():
                    chalani = form.save(commit=False)
                    chalani.created_by = request.user
                    # Explicitly set the fiscal_year to the active one for the new document
                    chalani.fiscal_year = active_fiscal_year_obj
                    chalani.save() # Model's save method will now use this fiscal_year for numbering
                messages.success(request, 'Chalani document added successfully!')
                return redirect('darta_chalani:chalani_detail', pk=chalani.pk)
            except ValidationError as e:
                messages.error(request, f'Error adding Chalani: {e.message}')
            except Exception as e:
                messages.error(request, f'An unexpected error occurred: {e}')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ChalaniForm()

    context = {
        'form': form,
        'title': 'Add New Chalani Document',
        'current_fiscal_year_name': active_fiscal_year_obj.name # Pass active fiscal year name to template
    }
    return render(request, 'darta_chalani/chalani_form.html', context)

@login_required
def chalani_detail(request, pk):
    """Displays details of a specific Chalani document and its single attachment."""
    chalani = get_object_or_404(Chalani, pk=pk)
    context = {
        'chalani': chalani,
        'title': f'Chalani Details: {chalani.document_number}'
    }
    return render(request, 'darta_chalani/chalani_detail.html', context)

@login_required
@permission_required('darta_chalani.change_chalani', raise_exception=True)
def chalani_edit(request, pk):
    """Handles editing an existing Chalani document and its single attachment."""
    chalani = get_object_or_404(Chalani, pk=pk)
    try:
        active_fiscal_year_obj = _get_active_fiscal_year()
    except ValidationError as e:
        messages.error(request, f'Configuration Error: {e.message}')
        return redirect('darta_chalani:chalani_detail', pk=pk)

    if request.method == 'POST':
        form = ChalaniForm(request.POST, request.FILES, instance=chalani)
        if form.is_valid():
            try:
                with transaction.atomic():
                    form.save()
                messages.success(request, 'Chalani document updated successfully!')
                return redirect('darta_chalani:chalani_detail', pk=chalani.pk)
            except ValidationError as e:
                messages.error(request, f'Error updating Chalani: {e.message}')
            except Exception as e:
                messages.error(request, f'An unexpected error occurred: {e}')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ChalaniForm(instance=chalani)

    context = {
        'form': form,
        'title': f'Edit Chalani: {chalani.document_number}',
        'current_fiscal_year_name': active_fiscal_year_obj.name # Pass active fiscal year name to template
    }
    return render(request, 'darta_chalani/chalani_form.html', context)

@login_required
@permission_required('darta_chalani.delete_chalani', raise_exception=True)
def chalani_delete(request, pk):
    """Handles deleting a Chalani document."""
    chalani = get_object_or_404(Chalani, pk=pk)
    if request.method == 'POST':
        try:
            chalani.delete()
            messages.success(request, 'Chalani document deleted successfully.')
            return redirect('darta_chalani:chalani_list')
        except Exception as e:
            messages.error(request, f'Error deleting Chalani: {e}')
            return redirect('darta_chalani:chalani_detail', pk=chalani.pk)
    context = {
        'chalani': chalani,
        'title': f'Confirm Delete Chalani: {chalani.document_number}'
    }
    return render(request, 'darta_chalani/chalani_confirm_delete.html', context)

# # darta_chalani/views.py
# from django.shortcuts import render, get_object_or_404, redirect
# from django.contrib.auth.decorators import login_required, permission_required
# from django.db import transaction
# from django.contrib import messages
# from django.core.exceptions import ValidationError
# from django.db.models import Max # Import Max for aggregation (though used in model.save now)

# from .models import Darta, Chalani
# from .forms import DartaForm, ChalaniForm

# # IMPORTANT: Import your FiscalYear model
# from settings_app.models import FiscalYear

# # --- Darta Views ---

# @login_required
# def darta_list(request):
#     """Lists all Darta (incoming) documents."""
#     dartas = Darta.objects.all().order_by('-document_date', '-created_at')
#     context = {
#         'dartas': dartas,
#         'title': 'Incoming Documents (Darta)'
#     }
#     return render(request, 'darta_chalani/darta_list.html', context)

# @login_required
# @permission_required('darta_chalani.add_darta', raise_exception=True)
# def darta_add(request):
#     """Handles adding a new Darta document with a single optional attachment."""
#     # Retrieve the active fiscal year to display it in the form
#     active_fiscal_year_obj = FiscalYear.objects.filter(is_active=True).first()
#     if not active_fiscal_year_obj:
#         messages.error(request, 'Error: No active Fiscal Year found. Please set one in settings to add new documents.')
#         # Redirect to a safer page, like the darta list, or an admin page
#         return redirect('darta_chalani:darta_list')

#     if request.method == 'POST':
#         form = DartaForm(request.POST, request.FILES)
#         if form.is_valid():
#             try:
#                 with transaction.atomic():
#                     darta = form.save(commit=False)
#                     darta.created_by = request.user
#                     # The fiscal_year and document_number auto-assignment logic is now handled
#                     # directly within the Darta model's save() method before it hits the DB.
#                     darta.save()
#                 messages.success(request, 'Darta document added successfully!')
#                 return redirect('darta_chalani:darta_detail', pk=darta.pk)
#             except ValidationError as e:
#                 # Catch ValidationErrors from the model's save method (e.g., no active fiscal year)
#                 messages.error(request, f'Error adding Darta: {e.message}')
#             except Exception as e:
#                 # Catch any other unexpected errors during save
#                 messages.error(request, f'An unexpected error occurred: {e}')
#         else:
#             messages.error(request, 'Please correct the errors below.')
#     else:
#         form = DartaForm()

#     context = {
#         'form': form,
#         'title': 'Add New Darta Document',
#         'current_fiscal_year_name': active_fiscal_year_obj.name # Pass active fiscal year name to template
#     }
#     return render(request, 'darta_chalani/darta_form.html', context)

# @login_required
# def darta_detail(request, pk):
#     """Displays details of a specific Darta document and its single attachment."""
#     darta = get_object_or_404(Darta, pk=pk)
#     context = {
#         'darta': darta,
#         'title': f'Darta Details: {darta.document_number}'
#     }
#     return render(request, 'darta_chalani/darta_detail.html', context)

# @login_required
# @permission_required('darta_chalani.change_darta', raise_exception=True)
# def darta_edit(request, pk):
#     """Handles editing an existing Darta document and its single attachment."""
#     darta = get_object_or_404(Darta, pk=pk)
#     # Retrieve the active fiscal year to display it in the form
#     active_fiscal_year_obj = FiscalYear.objects.filter(is_active=True).first()
#     # It's good practice to ensure one exists even for edits if you rely on it
#     if not active_fiscal_year_obj:
#         messages.error(request, 'Error: No active Fiscal Year found. Please set one in settings.')
#         return redirect('darta_chalani:darta_detail', pk=pk)


#     if request.method == 'POST':
#         form = DartaForm(request.POST, request.FILES, instance=darta)
#         if form.is_valid():
#             try:
#                 with transaction.atomic():
#                     form.save() # Model's save method handles fiscal_year and document_number if not provided
#                 messages.success(request, 'Darta document updated successfully!')
#                 return redirect('darta_chalani:darta_detail', pk=darta.pk)
#             except ValidationError as e:
#                 messages.error(request, f'Error updating Darta: {e.message}')
#             except Exception as e:
#                 messages.error(request, f'An unexpected error occurred: {e}')
#         else:
#             messages.error(request, 'Please correct the errors below.')
#     else:
#         form = DartaForm(instance=darta)

#     context = {
#         'form': form,
#         'title': f'Edit Darta: {darta.document_number}',
#         'current_fiscal_year_name': active_fiscal_year_obj.year_name # Pass active fiscal year name to template
#     }
#     return render(request, 'darta_chalani/darta_form.html', context)

# @login_required
# @permission_required('darta_chalani.delete_darta', raise_exception=True)
# def darta_delete(request, pk):
#     """Handles deleting a Darta document."""
#     darta = get_object_or_404(Darta, pk=pk)
#     if request.method == 'POST':
#         try:
#             darta.delete()
#             messages.success(request, 'Darta document deleted successfully.')
#             return redirect('darta_chalani:darta_list')
#         except Exception as e:
#             messages.error(request, f'Error deleting Darta: {e}')
#             return redirect('darta_chalani:darta_detail', pk=darta.pk)
#     context = {
#         'darta': darta,
#         'title': f'Confirm Delete Darta: {darta.document_number}'
#     }
#     return render(request, 'darta_chalani/darta_confirm_delete.html', context)

# # --- Chalani Views ---

# @login_required
# def chalani_list(request):
#     """Lists all Chalani (outgoing) documents."""
#     chalanis = Chalani.objects.all().order_by('-document_date', '-created_at')
#     context = {
#         'chalanis': chalanis,
#         'title': 'Outgoing Documents (Chalani)'
#     }
#     return render(request, 'darta_chalani/chalani_list.html', context)

# @login_required
# @permission_required('darta_chalani.add_chalani', raise_exception=True)
# def chalani_add(request):
#     """Handles adding a new Chalani document with a single optional attachment."""
#     # Retrieve the active fiscal year to display it in the form
#     active_fiscal_year_obj = FiscalYear.objects.filter(is_active=True).first()
#     if not active_fiscal_year_obj:
#         messages.error(request, 'Error: No active Fiscal Year found. Please set one in settings to add new documents.')
#         return redirect('darta_chalani:chalani_list')

#     if request.method == 'POST':
#         form = ChalaniForm(request.POST, request.FILES)
#         if form.is_valid():
#             try:
#                 with transaction.atomic():
#                     chalani = form.save(commit=False)
#                     chalani.created_by = request.user
#                     chalani.save()
#                 messages.success(request, 'Chalani document added successfully!')
#                 return redirect('darta_chalani:chalani_detail', pk=chalani.pk)
#             except ValidationError as e:
#                 messages.error(request, f'Error adding Chalani: {e.message}')
#             except Exception as e:
#                 messages.error(request, f'An unexpected error occurred: {e}')
#         else:
#             messages.error(request, 'Please correct the errors below.')
#     else:
#         form = ChalaniForm()

#     context = {
#         'form': form,
#         'title': 'Add New Chalani Document',
#         'current_fiscal_year_name': active_fiscal_year_obj.name # Pass active fiscal year name to template
#     }
#     return render(request, 'darta_chalani/chalani_form.html', context)


# @login_required
# def chalani_detail(request, pk):
#     """Displays details of a specific Chalani document and its single attachment."""
#     chalani = get_object_or_404(Chalani, pk=pk)
#     context = {
#         'chalani': chalani,
#         'title': f'Chalani Details: {chalani.document_number}'
#     }
#     return render(request, 'darta_chalani/chalani_detail.html', context)

# @login_required
# @permission_required('darta_chalani.change_chalani', raise_exception=True)
# def chalani_edit(request, pk):
#     """Handles editing an existing Chalani document and its single attachment."""
#     chalani = get_object_or_404(Chalani, pk=pk)
#     # Retrieve the active fiscal year to display it in the form
#     active_fiscal_year_obj = FiscalYear.objects.filter(is_active=True).first()
#     if not active_fiscal_year_obj:
#         messages.error(request, 'Error: No active Fiscal Year found. Please set one in settings.')
#         return redirect('darta_chalani:chalani_detail', pk=pk)

#     if request.method == 'POST':
#         form = ChalaniForm(request.POST, request.FILES, instance=chalani)
#         if form.is_valid():
#             try:
#                 with transaction.atomic():
#                     form.save()
#                 messages.success(request, 'Chalani document updated successfully!')
#                 return redirect('darta_chalani:chalani_detail', pk=chalani.pk)
#             except ValidationError as e:
#                 messages.error(request, f'Error updating Chalani: {e.message}')
#             except Exception as e:
#                 messages.error(request, f'An unexpected error occurred: {e}')
#         else:
#             messages.error(request, 'Please correct the errors below.')
#     else:
#         form = ChalaniForm(instance=chalani)

#     context = {
#         'form': form,
#         'title': f'Edit Chalani: {chalani.document_number}',
#         'current_fiscal_year_name': active_fiscal_year_obj.year_name # Pass active fiscal year name to template
#     }
#     return render(request, 'darta_chalani/chalani_form.html', context)

# @login_required
# @permission_required('darta_chalani.delete_chalani', raise_exception=True)
# def chalani_delete(request, pk):
#     """Handles deleting a Chalani document."""
#     chalani = get_object_or_404(Chalani, pk=pk)
#     if request.method == 'POST':
#         try:
#             chalani.delete()
#             messages.success(request, 'Chalani document deleted successfully.')
#             return redirect('darta_chalani:chalani_list')
#         except Exception as e:
#             messages.error(request, f'Error deleting Chalani: {e}')
#             return redirect('darta_chalani:chalani_detail', pk=chalani.pk)
#     context = {
#         'chalani': chalani,
#         'title': f'Confirm Delete Chalani: {chalani.document_number}'
#     }
#     return render(request, 'darta_chalani/chalani_confirm_delete.html', context)