from django import forms

from .models import BookingSheet, Campaign

class BookingSheetForm(forms.ModelForm):
    class Meta:
        model = BookingSheet
        fields = ['material', 'ad_type', 'start_date', 'end_date', 'time_slots']
        widgets = {
            'start_date': forms.DateInput(attrs={'class': 'date-input'}),
            'end_date': forms.DateInput(attrs={'class': 'date-input'}),
            'time_slots': forms.CheckboxSelectMultiple(),
        }

class CampaignForm(forms.ModelForm):
    class Meta:
        model = Campaign
        fields = ['client', 'ad_agency']
