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

    def test_equals(self):
        campaign = Campaign.objects.create(client='test client', ad_agency='test agency')
        time_slot = TimeSlot.objects.create(time=datetime.time(hour=8))
        fp = open('README.md','r')
        booking_sheet = BookingSheet(ad_type='REC',
                                     start_date=datetime.date(year=2018, month=4, day=2),
                                     end_date=datetime.date(year=2018, month=2, day=2),
                                     campaign=campaign,
                                     material=File(fp),
                                     cost=220)
        booking_sheet.save()
        booking_sheet.time_slots.add(time_slot)
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
        time_slot = TimeSlot.objects.create(time=datetime.time(hour=8))
        time_slot.save()
        cls.time_slot = { 1: time_slot.id }
        time_slot = TimeSlot.objects.create(time=datetime.time(hour=9))
        time_slot.save()
        cls.time_slot[2] = time_slot.id
        time_slot = TimeSlot.objects.create(time=datetime.time(hour=10))
        time_slot.save()
        cls.time_slot[3] = time_slot.id
        time_slot = TimeSlot.objects.create(time=datetime.time(hour=11))
        time_slot.save()
        cls.time_slot[4] = time_slot.id
        form_data = {'ad_type': 'REC',
                     'start_date': '2018-05-07',
                     'end_date': '2018-05-21',
                     'cost': '200',
                     'time_slots': [str(cls.time_slot[1]),str(cls.time_slot[3])],
                     'time_slot_flexiblility': '1'}
        booking = BookingSheet(campaign=campaign, material=File(cls.fp))
        cls.form = BookingSheetForm(data=form_data, instance=booking)

    @classmethod
    def tearDownClass(cls):
        cls.fp.close()
        super().tearDownClass()

    def test_validate_form(self):
        self.assertTrue(self.form.is_valid())
        time_slots = TimeSlot.objects.filter(id__in=[self.time_slot[1], self.time_slot[3]])
        self.assertEquals(self.form.cleaned_data['time_slots'].order_by('time')[0],
                                 time_slots.order_by('time')[0])
        self.assertEquals(self.form.cleaned_data['time_slots'].order_by('time')[1],
                                 time_slots.order_by('time')[1])

    def test_shift_time_slot(self):
        campaign = Campaign.objects.create(client='test client', ad_agency='test agency')
        campaign.save()
        fp = open('README.md','r')
        form_data = {'ad_type': 'REC',
                     'start_date': '2018-05-07',
                     'end_date': '2018-05-21',
                     'cost': '200',
                     'time_slots': [str(self.time_slot[1]),str(self.time_slot[3])],
                     'time_slot_flexiblility': '1'}
        booking = BookingSheet(campaign=campaign, material=File(fp))
        form = BookingSheetForm(data=form_data, instance=booking)
        form.save()

        current_bookings = BookingSheet.objects.filter(time_slots__id=self.time_slot[1])
        self.assertEquals(current_bookings.count(), 1)

        self.form.is_valid()
        time_slots = TimeSlot.objects.filter(id__in=[self.time_slot[2], self.time_slot[4]])
        self.assertEquals(self.form.cleaned_data['time_slots'].order_by('time')[0],
                                 time_slots.order_by('time')[0])
        self.assertEquals(self.form.cleaned_data['time_slots'].order_by('time')[1],
                                 time_slots.order_by('time')[1])
        self.assertEquals(self.form.cleaned_data['time_slot_flexiblility'], 0)

