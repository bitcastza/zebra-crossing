import datetime
from django.core.exceptions import ValidationError
from django.core.files import File
from django.test import TestCase, Client
from django.utils.translation import gettext_lazy as _
from django.urls import reverse

from .models import BookingSheet, Campaign, TimeSlot, BookedDay
from .forms import BookingSheetForm
from django.test.client import RequestFactory
from .views import save_to_table
import json


class TimeSlotTests(TestCase):
    def test_to_string(self):
        time_slot = TimeSlot(time=datetime.time(hour=8))
        expected = datetime.time(hour=8).strftime("%H:%M")
        self.assertEqual(time_slot.__str__(), expected)

    def test_equals(self):
        time_slot = TimeSlot(time=datetime.time(hour=8))
        other = TimeSlot(time=datetime.time(hour=8))
        self.assertEqual(time_slot, other)


class SaveToTableTest(TestCase):
    @classmethod
    def setUp(self):
        self.client = Client()
        self.save_to_table_url = reverse("campaigns:save_to_table")
        self.fp = open("README.md")
        campaign = Campaign.objects.create(
            client="test client", ad_agency="test agency"
        )
        self.booking_sheet = BookingSheet(
            ad_type="REC",
            start_date=datetime.date(year=2022, month=6, day=20),
            end_date=datetime.date(year=2022, month=7, day=31),
            campaign=campaign,
            booking_sheet=File(self.fp),
            cost=23000,
        )
        self.booking_sheet.save()

        self.time_slot = TimeSlot(time=datetime.time(hour=12, minute=53))
        self.time_slot.save()

        self.booked_day = BookedDay.objects.create(
            date=datetime.date(2022, 6, 25),
            timeslot=self.time_slot,
            bookingsheet=self.booking_sheet,
        )
        self.booked_day.save()

    def test_save_to_table(self):
        dict_expected = {
            "slot_time": "12:53",
            "date": "Saturday (25/06)",
            "bookingsheet_id": f"{self.booking_sheet.id}",
        }
        response = self.client.post(self.save_to_table_url, dict_expected, follow=True)

        self.assertEqual(str(self.booked_day.timeslot), "12:53")
        self.assertEqual(str(self.booked_day.date), "2022-06-25")
        self.assertEqual(self.booked_day.bookingsheet.cost, 23000)
        self.assertAlmostEqual(response.status_code, 200)

    @classmethod
    def tearDownClass(self):
        self.fp.close()
        super().tearDownClass()


class BookingSheetTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        campaign = Campaign.objects.create(
            client="test client", ad_agency="test agency"
        )
        cls.fp = open("README.md")
        cls.booking_sheet = BookingSheet(
            ad_type="REC",
            start_date=datetime.date(year=2018, month=4, day=2),
            end_date=datetime.date(year=2018, month=2, day=2),
            campaign=campaign,
            booking_sheet=File(cls.fp),
            cost=220,
        )
        cls.booking_sheet.save()

    @classmethod
    def tearDownClass(cls):
        cls.fp.close()
        super().tearDownClass()

    def test_clean_fields_start_after_end_exclude(self):
        with self.assertRaisesMessage(ValidationError, "Start date is after end date"):
            self.booking_sheet.clean_fields(exclude=["start_date"])

    def test_clean_fields_start_after_end(self):
        with self.assertRaisesMessage(ValidationError, "Start date is after end date"):
            self.booking_sheet.clean_fields()

    def test_equals(self):
        campaign = Campaign.objects.create(
            client="test client", ad_agency="test agency"
        )
        fp = open("README.md")
        booking_sheet = BookingSheet(
            ad_type="REC",
            start_date=datetime.date(year=2018, month=4, day=2),
            end_date=datetime.date(year=2018, month=2, day=2),
            campaign=campaign,
            booking_sheet=File(fp),
            cost=220,
        )
        booking_sheet.save()
        self.assertEqual(self.booking_sheet, booking_sheet)


class CampaignTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.campaign = Campaign.objects.create(
            client="test client", ad_agency="test agency"
        )
        cls.campaign.save()

    def test_equals(self):
        campaign = Campaign.objects.create(
            client="test client", ad_agency="test agency"
        )
        campaign.save()
        self.assertEqual(self.campaign, campaign)


class BookingSheetFormTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        campaign = Campaign.objects.create(
            client="test client", ad_agency="test agency"
        )
        campaign.save()
        cls.fp = open("README.md")
        form_data = {
            "ad_type": "REC",
            "start_date": "2018-05-07",
            "end_date": "2018-05-21",
            "cost": "200",
            "campaign": campaign,
        }
        booking = BookingSheet(campaign=campaign, booking_sheet=File(cls.fp))
        cls.form = BookingSheetForm(data=form_data, instance=booking)

    @classmethod
    def tearDownClass(cls):
        cls.fp.close()
        super().tearDownClass()

    def test_validate_form(self):
        self.assertTrue(self.form.is_valid())
