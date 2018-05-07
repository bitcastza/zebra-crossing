import datetime
from django.core.exceptions import ValidationError
from django.core.files import File
from django.test import TestCase
from django.utils.translation import gettext_lazy as _

from .models import BookingSheet, Campaign, TimeSlot

class TimeSlotTests(TestCase):
    def test_to_string(self):
        time_slot = TimeSlot(time=datetime.time(hour=8))
        expected = datetime.time(hour=8).strftime("%H:%M")
        self.assertEqual(time_slot.__str__(), expected)

class BookingSheetTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        campaign = Campaign.objects.create(client='test client', ad_agency='test agency')
        time_slot = TimeSlot.objects.create(time=datetime.time(hour=8))
        cls.fp = open('README.md','r')
        cls.booking_sheet = BookingSheet(ad_type='REC',
                                     start_date=datetime.date(year=2018, month=4, day=2),
                                     end_date=datetime.date(year=2018, month=2, day=2),
                                     campaign=campaign,
                                     material=File(cls.fp),
                                     cost=220)
        cls.booking_sheet.save()
        cls.booking_sheet.time_slots.add(time_slot)

    @classmethod
    def tearDownClass(cls):
        cls.fp.close()
        super().tearDownClass()

    def test_clean_fields_start_after_end_exclude(self):
        with self.assertRaisesMessage(ValidationError, "Start date is after end date"):
            self.booking_sheet.clean_fields(exclude=['start_date'])

    def test_clean_fields_start_after_end(self):
        with self.assertRaisesMessage(ValidationError, "Start date is after end date"):
            self.booking_sheet.clean_fields()
