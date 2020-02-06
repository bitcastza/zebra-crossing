import datetime
from django.core.exceptions import ValidationError
from django.core.files import File
from django.test import TestCase
from django.utils.translation import gettext_lazy as _

from .models import BookingSheet, Campaign, TimeSlot
from .forms import BookingSheetForm

class TimeSlotTests(TestCase):
    def test_to_string(self):
        time_slot = TimeSlot(time=datetime.time(hour=8))
        expected = datetime.time(hour=8).strftime("%H:%M")
        self.assertEqual(time_slot.__str__(), expected)

    def test_equals(self):
        time_slot = TimeSlot(time=datetime.time(hour=8))
        other = TimeSlot(time=datetime.time(hour=8))
        self.assertEqual(time_slot, other)

class BookingSheetTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        campaign = Campaign.objects.create(client='test client', ad_agency='test agency')
        cls.fp = open('README.md','r')
        cls.booking_sheet = BookingSheet(ad_type='REC',
                                     start_date=datetime.date(year=2018, month=4, day=2),
                                     end_date=datetime.date(year=2018, month=2, day=2),
                                     campaign=campaign,
                                     booking_sheet=File(cls.fp),
                                     cost=220)
        cls.booking_sheet.save()

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

    def test_equals(self):
        campaign = Campaign.objects.create(client='test client', ad_agency='test agency')
        fp = open('README.md','r')
        booking_sheet = BookingSheet(ad_type='REC',
                                     start_date=datetime.date(year=2018, month=4, day=2),
                                     end_date=datetime.date(year=2018, month=2, day=2),
                                     campaign=campaign,
                                     booking_sheet=File(fp),
                                     cost=220)
        booking_sheet.save()
        self.assertEqual(self.booking_sheet, booking_sheet)

class CampaignTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.campaign = Campaign.objects.create(client='test client',
                                               ad_agency='test agency')
        cls.campaign.save()

    def test_equals(self):
        campaign = Campaign.objects.create(client='test client',
                                               ad_agency='test agency')
        campaign.save()
        self.assertEquals(self.campaign, campaign)

class BookingSheetFormTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        campaign = Campaign.objects.create(client='test client', ad_agency='test agency')
        campaign.save()
        cls.fp = open('README.md','r')
        form_data = {'ad_type': 'REC',
                     'start_date': '2018-05-07',
                     'end_date': '2018-05-21',
                     'cost': '200',}
        booking = BookingSheet(campaign=campaign, booking_sheet=File(cls.fp))
        cls.form = BookingSheetForm(data=form_data, instance=booking)

    @classmethod
    def tearDownClass(cls):
        cls.fp.close()
        super().tearDownClass()

    def test_validate_form(self):
        self.assertTrue(self.form.is_valid())
