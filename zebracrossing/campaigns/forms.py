from django import forms

from .models import BookingSheet

class BookingSheetForm(forms.ModelForm):
    class Meta:
        model = BookingSheet
        fields = ['material', 'ad_type', 'start_date', 'end_date']
