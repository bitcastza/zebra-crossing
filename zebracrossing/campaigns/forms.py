from django import forms

from zebracrossing.forms import CalendarWidget
from .models import BookingSheet, Campaign, TimeSlot, Material


class BookingSheetForm(forms.ModelForm):
    class Meta:
        model = BookingSheet
        fields = [
            "booking_sheet",
            "ad_type",
            "start_date",
            "end_date",
            "cost",
            "campaign",
        ]
        widgets = {
            "start_date": CalendarWidget,
            "end_date": CalendarWidget,
            "campaign": forms.HiddenInput(),
        }


class CampaignForm(forms.ModelForm):
    class Meta:
        model = Campaign
        fields = ["client", "ad_agency"]


class MaterialForm(forms.ModelForm):
    class Meta:
        model = Material
        fields = ["material", "campaign"]
        widgets = {"campaign": forms.HiddenInput()}
