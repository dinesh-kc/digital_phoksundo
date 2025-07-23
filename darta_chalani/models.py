# darta_chalani/models.py
from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.urls import reverse
from django.urls import reverse
from django.db.models import Max # Import Max for aggregation

# IMPORTANT: Import your FiscalYear model from where it's defined
from settings_app.models import FiscalYear # Assuming settings_app contains Department and FiscalYear

User = get_user_model()


class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Department"
        verbose_name_plural = "Departments"
        ordering = ['name']

    def __str__(self):
        return self.name
 





# --- Common Choices/Constants ---
DOCUMENT_TYPE_CHOICES = [
    ('Letter', 'Letter'),
    ('Notice', 'Notice'),
    ('Report', 'Report'),
    ('Application', 'Application'),
    ('Other', 'Other'),
]

# --- Abstract Base Document Model ---
class Document(models.Model):
    # document_number should NOT be unique=True at the model level if it's generated
    # The uniqueness will be enforced by a combination of document_number and fiscal_year
    document_number = models.CharField(max_length=100, help_text="Unique number within its fiscal year.")
    subject = models.CharField(max_length=255)
    document_date = models.DateField(default=timezone.now)
    fiscal_year = models.ForeignKey(FiscalYear, on_delete=models.PROTECT,
                                    related_name='%(app_label)s_%(class)s_documents',
                                    help_text="The fiscal year of the document.")
    sender_receiver_info = models.CharField(max_length=255, help_text="Sender's details for Darta, Receiver's details for Chalani.")
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name='%(app_label)s_%(class)s_documents')
    document_type = models.CharField(max_length=50, choices=DOCUMENT_TYPE_CHOICES, default='Letter')
    is_confidential = models.BooleanField(default=False)
    expiry_date = models.DateField(null=True, blank=True, help_text="Date after which the document might not be relevant.")
    followup_date = models.DateField(null=True, blank=True, help_text="Date for necessary follow-up action.")
    remarks = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name='%(app_label)s_%(class)s_created_documents')

    class Meta:
        abstract = True
        ordering = ['-document_date', '-created_at']
        # Add a unique_together constraint to ensure unique numbers per fiscal year
        unique_together = [['document_number', 'fiscal_year']]

    def __str__(self):
        return f"{self.document_number} - {self.subject} ({self.fiscal_year.year_name})"

    def clean(self):
        if self.expiry_date and self.document_date and self.expiry_date < self.document_date:
            raise ValidationError({'expiry_date': "Expiry date cannot be before the document date."})
        if self.followup_date and self.document_date and self.followup_date < self.document_date:
            raise ValidationError({'followup_date': "Follow-up date cannot be before the document date."})

    def save(self, *args, **kwargs):
        # 1. Ensure an active fiscal year exists and is assigned
        active_fiscal_year_obj = FiscalYear.objects.filter(is_active=True).first()
        if not active_fiscal_year_obj:
            raise ValidationError('No active Fiscal Year found. Please set one in settings.')

        # If fiscal_year is not set on the document, automatically assign the active one
        if not self.fiscal_year_id:
            self.fiscal_year = active_fiscal_year_obj

        # 2. Generate document_number if it's a new record and not already set
        if not self.pk and not self.document_number: # For new objects and if document_number is empty
            model_class = self.__class__ # Darta or Chalani
            # Get the max document_number for the current fiscal year for this model type
            last_number = model_class.objects.filter(fiscal_year=self.fiscal_year).aggregate(Max('document_number'))['document_number__max']

            if last_number:
                # Assuming numbers are purely numeric or can be converted to int
                try:
                    next_number = int(last_number) + 1
                except ValueError:
                    # Handle cases where document_number might not be purely numeric
                    # For simplicity, if not numeric, restart from 1 or handle as error
                    next_number = 1
                    # You might want a more sophisticated parsing or error handling here
            else:
                next_number = 1
            self.document_number = str(next_number)

        self.full_clean() # Run full model validation (including clean method)
        super().save(*args, **kwargs)


# --- Darta Model ---
class Darta(Document):
    attachment_file = models.FileField(upload_to='darta_files/', null=True, blank=True,
                                      help_text="Upload the main document file.")

    class Meta(Document.Meta):
        verbose_name = "Darta"
        verbose_name_plural = "Dartas"
        default_related_name = 'darta_documents'
        # unique_together inherited from Document

    def get_absolute_url(self):
        return reverse('darta_chalani:darta_detail', kwargs={'pk': self.pk})

# --- Chalani Model ---
class Chalani(Document):
    attachment_file = models.FileField(upload_to='chalani_files/', null=True, blank=True,
                                      help_text="Upload the main document file.")

    class Meta(Document.Meta):
        verbose_name = "Chalani"
        verbose_name_plural = "Chalanis"
        default_related_name = 'chalani_documents'
        # unique_together inherited from Document

    def get_absolute_url(self):
        return reverse('darta_chalani:chalani_detail', kwargs={'pk': self.pk})