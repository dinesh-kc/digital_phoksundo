# settings_app/models.py
from django.db import models
from django.core.exceptions import ValidationError
from django.db.models.signals import pre_save
from django.dispatch import receiver
import nepali_datetime
from datetime import date as dt_date # Alias datetime.date to avoid conflict


class FiscalYear(models.Model):
    """
    Represents a fiscal year, e.g., 2081/82 BS or 2024/2025 AD.
    Only one fiscal year should be marked as active at any time.
    """
    # Store AD dates in the database
    start_date_ad = models.DateField(
        unique=True, 
        help_text="Start date of the fiscal year in AD (e.g., 2023-07-16 for 2080/81 BS)"
    )
    end_date_ad = models.DateField(
        unique=True, 
        help_text="End date of the fiscal year in AD (e.g., 2024-07-15 for 2080/81 BS)"
    )
    # 'name' will be auto-generated based on Nepali dates
    name = models.CharField(
        max_length=20, 
        unique=True, 
        blank=True, # Allow blank as it will be auto-generated
        null=True,  # Allow null as it will be auto-generated
        help_text="Nepali Fiscal Year Name (e.g., 2080/81 BS). Will be auto-generated if left blank."
    )
    is_active = models.BooleanField(
        default=False, 
        help_text="Set as the currently active fiscal year for Darta/Chalani. Only one can be active."
    )

    class Meta:
        verbose_name = "Fiscal Year"
        verbose_name_plural = "Fiscal Years"
        ordering = ['-start_date_ad'] # Order by most recent first

    def __str__(self):
        # Prefer the generated Nepali display name, fallback to stored name, then AD dates
        return self.get_nepali_year_display() or self.name or f"FY: {self.start_date_ad} - {self.end_date_ad}"

    def clean(self):
        # Ensure start_date_ad is before end_date_ad
        if self.start_date_ad and self.end_date_ad and self.start_date_ad >= self.end_date_ad:
            raise ValidationError({'end_date_ad': "End date must be after the start date."})

        # The unique active constraint is handled by the pre_save signal for automatic deactivation.
        # However, if you want a validation error *before* save (e.g., in admin),
        # you could uncomment the following, but it might conflict with the signal's
        # auto-deactivation logic if not carefully managed.
        # For simplicity and robust auto-deactivation, we rely on the signal.
        # if self.is_active:
        #     qs = FiscalYear.objects.filter(is_active=True)
        #     if self.pk:
        #         qs = qs.exclude(pk=self.pk)
        #     if qs.exists():
        #         raise ValidationError("Another Fiscal Year is already active. Please deactivate it first or uncheck 'is_active'.")

    def save(self, *args, **kwargs):
        # Call full_clean() to run model-level validation (like start_date < end_date)
        self.full_clean()

        # Auto-generate or update the 'name' field based on AD dates if not provided or if dates change
        if self.start_date_ad and self.end_date_ad:
            try:
                np_start_date = nepali_datetime.date.from_datetime_date(self.start_date_ad)
                np_end_date = nepali_datetime.date.from_datetime_date(self.end_date_ad)
                
                # Nepali fiscal year typically starts on Shrawan 1 (approx July 16)
                # The name is derived from the Nepali year of the start date and the last two digits of the end date.
                self.name = f"{np_start_date.year}/{str(np_end_date.year)[-2:]}"
            except nepali_datetime.NepaliDateError:
                # Fallback if AD date conversion fails (e.g., date out of Nepali calendar range)
                if not self.name: # Only set a fallback name if it's not already set
                    self.name = f"FY-{self.start_date_ad.year}" 
        
        super().save(*args, **kwargs)

    def get_nepali_year_display(self):
        """
        Returns the Nepali fiscal year string (e.g., '2080/81 BS') based on its AD dates.
        This is the preferred display method.
        """
        if self.start_date_ad and self.end_date_ad:
            try:
                np_start_date = nepali_datetime.date.from_datetime_date(self.start_date_ad)
                np_end_date = nepali_datetime.date.from_datetime_date(self.end_date_ad)
                return f"{np_start_date.year}/{str(np_end_date.year)[-2:]} BS"
            except nepali_datetime.NepaliDateError:
                return "Invalid BS Date"
        return "N/A"

    def get_nepali_start_date(self):
        """Returns the Nepali start date object (nepali_datetime.date)."""
        if self.start_date_ad:
            try:
                return nepali_datetime.date.from_datetime_date(self.start_date_ad)
            except nepali_datetime.NepaliDateError:
                return None
        return None

    def get_nepali_end_date(self):
        """Returns the Nepali end date object (nepali_datetime.date)."""
        if self.end_date_ad:
            try:
                return nepali_datetime.date.from_datetime_date(self.end_date_ad)
            except nepali_datetime.NepaliDateError:
                return None
        return None

# Signal to ensure only one fiscal year is active at a time
@receiver(pre_save, sender=FiscalYear)
def ensure_single_active_fiscal_year(sender, instance, **kwargs):
    """
    Deactivates all other fiscal years if the current one is being set to active.
    This runs *before* the instance is saved.
    """
    if instance.is_active:
        # Deactivate all other fiscal years excluding the current instance
        # Use update() to avoid calling save() on other instances, preventing recursion
        sender.objects.filter(is_active=True).exclude(pk=instance.pk).update(is_active=False)