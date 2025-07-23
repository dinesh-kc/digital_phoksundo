# darta_chalani/forms.py
from django import forms
from .models import Darta, Chalani
import nepali_datetime
from datetime import date as dt_date

class NepaliDateField(forms.CharField):
    def to_python(self, value):
        if not value:
            return None
        if isinstance(value, dt_date):
            return value
        try:
            y, m, d = map(int, value.split('-'))
            np_date = nepali_datetime.date(y, m, d)
            return np_date.to_datetime_date()  # Save AD in DB
        except Exception:
            raise forms.ValidationError("Invalid Nepali date format (YYYY-MM-DD)")
        
    # print("Prepare value:", value)

    def prepare_value(self, value):
        if isinstance(value, dt_date):
            try:
                np_date = nepali_datetime.date.from_datetime_date(value)
                return np_date.strftime('%Y-%m-%d')
            except Exception:
                return ''
        return value

class BaseFormWithNepaliDates(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name in ['document_date', 'expiry_date', 'followup_date']:
            if field_name in self.fields:
                self.fields[field_name].widget.attrs['class'] = 'form-control date-picker'
                self.fields[field_name].widget.attrs.pop('readonly', None)
                self.fields[field_name].widget.attrs['placeholder'] = 'Select a Nepali date'

class DartaForm(BaseFormWithNepaliDates):
    document_date = NepaliDateField(label="Document Date (BS)")
    expiry_date = NepaliDateField(label="Expiry Date (BS)", required=False)
    followup_date = NepaliDateField(label="Follow-up Date (BS)", required=False)

    document_number = forms.CharField(
        label="Darta Number",
        required=False,
        widget=forms.TextInput(attrs={'readonly': 'readonly', 'placeholder': 'Auto-generated'})
    )

    class Meta:
        model = Darta
        fields = [
            'document_number', 'subject', 'document_date', 'sender_receiver_info',
            'department', 'document_type', 'is_confidential', 'expiry_date',
            'followup_date', 'remarks', 'attachment_file'
        ]
        widgets = {
            'subject': forms.TextInput(attrs={'class': 'form-control'}),
            'sender_receiver_info': forms.TextInput(attrs={'class': 'form-control'}),
            'department': forms.Select(attrs={'class': 'form-select'}),
            'document_type': forms.Select(attrs={'class': 'form-select'}),
            'is_confidential': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'remarks': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'attachment_file': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

class ChalaniForm(BaseFormWithNepaliDates):
    document_date = NepaliDateField(label="Document Date (BS)")
    expiry_date = NepaliDateField(label="Expiry Date (BS)", required=False)
    followup_date = NepaliDateField(label="Follow-up Date (BS)", required=False)

    document_number = forms.CharField(
        label="Chalani Number",
        required=False,
        widget=forms.TextInput(attrs={'readonly': 'readonly', 'placeholder': 'Auto-generated'})
    )

    sender_receiver_info = forms.CharField(
        label="Receiver Details",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Receiver Office or Person'})
    )

    class Meta:
        model = Chalani
        fields = [
            'document_number', 'subject', 'document_date', 'sender_receiver_info',
            'department', 'document_type', 'is_confidential', 'expiry_date',
            'followup_date', 'remarks', 'attachment_file'
        ]
        widgets = {
            'subject': forms.TextInput(attrs={'class': 'form-control'}),
            'department': forms.Select(attrs={'class': 'form-select'}),
            'document_type': forms.Select(attrs={'class': 'form-select'}),
            'is_confidential': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'remarks': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'attachment_file': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field_name in ['document_date', 'expiry_date', 'followup_date']:
            self.fields[field_name].widget.attrs.pop('readonly', None)
            self.fields[field_name].widget.attrs['class'] += ' date-picker'
