from django import forms

from zebracrossing.forms import CalendarWidget, FileWidget
from .models import BookingSheet, Campaign, TimeSlot, Material


class BookingSheetForm(forms.ModelForm):
    class Meta:
        model = BookingSheet
        fields = ['booking_sheet', 'ad_type', 'start_date', 'end_date', 'cost']
        widgets = {
            'booking_sheet': FileWidget,
            'start_date': CalendarWidget,
            'end_date': CalendarWidget,
        }


class CampaignForm(forms.ModelForm):
    class Meta:
        model = Campaign
        fields = ['client', 'ad_agency']


class MaterialForm(forms.ModelForm):
    class Meta:
        model = Material
        fields = ['material',]
        widgets = {
            'material': FileWidget,
        }
