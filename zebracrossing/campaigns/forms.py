from django import forms

from zebracrossing.forms import CalendarWidget, FileWidget
from .models import BookingSheet, Campaign, TimeSlot


class BookingSheetForm(forms.ModelForm):
    class Meta:
        model = BookingSheet
        fields = ['material', 'ad_type', 'start_date', 'end_date', 'cost']
        widgets = {
            'material': FileWidget,
            'start_date': CalendarWidget,
            'end_date': CalendarWidget,
        }

    def clean(self):
        cleaned_data = super().clean()
        old_cleaned_data = cleaned_data
        return cleaned_data

    def clean_time_slots_UNUSED(cleaned_data):
        """
        Places ads in time slots based on the provided times and flexibility. It
        is currently unused because it needs a better way of displaying
        timeslots and allowing them to be selected. Once that is fixed, this
        should be called from clean().
        """
        for slot in old_cleaned_data['time_slots']:
            current_bookings = BookingSheet.objects.filter(time_slots__time=slot.time)
            if current_bookings.count() > 0:
                time_slots = TimeSlot.objects.all().order_by('time')
                flexibility = cleaned_data.get('time_slot_flexiblility')
                index = 0
                for start_time_slot in time_slots:
                    if (start_time_slot == slot):
                        break
                    index += 1
                if (index >= time_slots.count()):
                    index = time_slots.count() - 1
                end_index = min(time_slots.count(), index + flexibility + 1)
                time_slots = time_slots[index:end_index]
                min_slot = slot
                for start_time_slot in time_slots:
                    current_min = BookingSheet.objects.filter(time_slots__time=min_slot.time)
                    bookings = BookingSheet.objects.filter(time_slots__time=start_time_slot.time)
                    if bookings.count() < current_min.count():
                        min_slot = start_time_slot
                cleaned_data['time_slots'].filter(id=slot.id).update(time=min_slot.time)
        cleaned_data['time_slot_flexiblility'] = 0


class CampaignForm(forms.ModelForm):
    class Meta:
        model = Campaign
        fields = ['client', 'ad_agency']
