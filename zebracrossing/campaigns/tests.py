import datetime
from django.core.exceptions import ValidationError
from django.core.files import File
from django.test import TestCase, Client
from django.utils.translation import gettext_lazy as _
from django.urls import reverse

from .models import BookingSheet, Campaign, TimeSlot, BookedDay
from .forms import BookingSheetForm
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
        self.campaign = Campaign.objects.create(
            client="Telkom", ad_agency="Telkom agency"
        )
        self.booking_sheet = BookingSheet(
            ad_type="REC",
            start_date=datetime.date(year=2022, month=6, day=20),
            end_date=datetime.date(year=2022, month=7, day=31),
            campaign=self.campaign,
            booking_sheet=File(self.fp),
            cost=23000,
        )
        self.booking_sheet.save()

        self.time_slot = TimeSlot(time=datetime.time(hour=12, minute=53))
        self.time_slot.save()

        self.booked_day = BookedDay.objects.create(
            date=datetime.date(2022, 6, 22),
            timeslot=self.time_slot,
            bookingsheet=self.booking_sheet,
        )

    def test_save_to_table(self):
        ajax_data_expected = [
            {"slot_time": "12:53", "date": "Wednesday (22/06)", "bookingsheet_id": "1"}
        ]
        response = self.client.post(
            self.save_to_table_url,
            ajax_data_expected,
            content_type="application/json",
        )

        self.assertEqual(
            BookingSheet.objects.get(start_date=self.booking_sheet.start_date),
            self.booking_sheet,
        )
        self.assertEqual(TimeSlot.objects.get(time=self.time_slot.time), self.time_slot)
        self.assertEqual(
            Campaign.objects.get(client=self.campaign.client), self.campaign
        )
        self.assertEqual(
            BookedDay.objects.get(date=self.booked_day.date), self.booked_day
        )
        self.assertEqual(response.status_code, 200)

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
