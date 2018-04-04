import datetime
from django.core.exceptions import ValidationError
from django.core.files import File
from django.test import TestCase
from django.utils.translation import gettext_lazy as _

from .models import BookingSheet, Campaign, TimeSlot

class TimeSlotTests(TestCase):
    def test_to_string(self):
        time_slot = TimeSlot(start_time=datetime.time(hour=8),
                             end_time=datetime.time(hour=9))
        expected = datetime.time(hour=8).strftime("%H:%M") + " - " + \
                datetime.time(hour=9).strftime("%H:%M")
        self.assertEqual(time_slot.__str__(), expected)

class BookingSheetTests(TestCase):
    def test_clean_fields_start_after_end_exclude(self):
        campaign = Campaign(client='test client', ad_agency='test agency')
        booking_sheet = BookingSheet(ad_type='REC',
                                     start_date=datetime.date(year=2018, month=4, day=2),
                                     end_date=datetime.date(year=2018, month=2, day=2),
                                     # TODO: Fix this...
                                     campaign=campaign,
                                     material=File("test file"))
        with self.assertRaisesMessage(ValidationError, _("Start date is after end date")):
            booking_sheet.clean_fields()
