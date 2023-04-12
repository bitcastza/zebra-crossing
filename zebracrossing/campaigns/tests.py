import datetime
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.files import File
from django.test import TestCase, Client
from django.urls import reverse
import json

from .models import BookingSheet, Campaign, TimeSlot, BookedDay
from .forms import BookingSheetForm
from django.contrib.auth.models import User


class TimeSlotTests(TestCase):
    def test_to_string(self):
        time_slot = TimeSlot(time=datetime.time(hour=8))
        expected = datetime.time(hour=8).strftime("%H:%M")
        self.assertEqual(time_slot.__str__(), expected)

    def test_equals(self):
        time_slot = TimeSlot(time=datetime.time(hour=8))
        other = TimeSlot(time=datetime.time(hour=8))
        self.assertEqual(time_slot, other)


class SaveScheduleTests(TestCase):
    @classmethod
    def setUp(cls):
        cls.fp = open("README.md")
        cls.campaign = Campaign.objects.create(
            client="Telkom", ad_agency="Telkom agency"
        )
        cls.booking_sheet = BookingSheet(
            ad_type="REC",
            start_date=datetime.date(year=2022, month=6, day=20),
            end_date=datetime.date(year=2022, month=7, day=31),
            campaign=cls.campaign,
            booking_sheet=File(cls.fp),
            cost=23000,
        )
        cls.booking_sheet.save()
        cls.time_slot = TimeSlot(time=datetime.time(hour=12, minute=53))
        cls.time_slot.save()
        cls.booked_day = BookedDay(
            date=datetime.date(2022, 6, 22),
            timeslot=cls.time_slot,
            bookingsheet=cls.booking_sheet,
        )

        cls.client = Client()
        cls.save_schedule_url = reverse(
            "campaigns:save_schedule", kwargs={"pk": cls.campaign.pk}
        )
        cls.user = get_user_model().objects.create_user(
            username="test", password="test"
        )

    def test_save_schedule_empty(self):
        self.client.login(username="test", password="test")
        response = self.client.post(self.save_schedule_url, {"schedule": [{}]})
        self.assertEqual(response.status_code, 400)

    def test_save_schedule_404(self):
        expected_data = json.dumps(
            [
                {
                    "slot_time": f"{self.time_slot.time}",
                    "date": self.booked_day.date.isoformat(),
                    "bookingsheet_id": self.booking_sheet.id + 1,
                }
            ]
        )
        self.client.login(username="test", password="test")
        response = self.client.post(self.save_schedule_url, {"schedule": expected_data})

        self.assertEqual(response.status_code, 404)

    def test_save_schedule(self):
        expected_data = json.dumps(
            [
                {
                    "slot_time": f"{self.time_slot.time}",
                    "date": self.booked_day.date.isoformat(),
                    "bookingsheet_id": self.booking_sheet.id,
                }
            ]
        )
        self.client.login(username="test", password="test")
        response = self.client.post(self.save_schedule_url, {"schedule": expected_data})
        self.assertEqual(response.status_code, 200)
        booking = BookedDay.objects.get(
            date=self.booked_day.date, timeslot=self.time_slot
        )
        self.assertEqual(booking.date, self.booked_day.date)
        self.assertEqual(booking.timeslot, self.booked_day.timeslot)
        self.assertEqual(booking.bookingsheet, self.booked_day.bookingsheet)

    @classmethod
    def tearDownClass(cls):
        cls.fp.close()
        super().tearDownClass()


class APIEndpointTests(TestCase):
    @classmethod
    def setUp(self):
        self.client = Client()
        self.start_date = "2022-07-07"
        self.end_date = "2022-07-08"
        self.schedule_list = [
            {
                "campaign": "Telkom",
                "material": {"download_url": "", "type": "REC"},
                "scheduled": "2022-07-07:07:40",
            }
        ]
        self.url = f"/api/v1/schedule/?start={self.start_date}&end={self.end_date}"

        campaign = Campaign.objects.create(client="Telkom", ad_agency="Telkom agency")
        self.fp = open("README.md")
        self.booking_sheet = BookingSheet(
            ad_type="REC",
            start_date=datetime.date(year=2022, month=7, day=7),
            end_date=datetime.date(year=2022, month=7, day=8),
            campaign=campaign,
            booking_sheet=File(self.fp),
            cost=23000,
        )
        self.booking_sheet.save()

        self.time_slot = TimeSlot(time=datetime.time(hour=7, minute=40))
        self.time_slot.save()

        self.bookedday = BookedDay(
            date="2022-07-07", timeslot=self.time_slot, bookingsheet=self.booking_sheet
        )
        self.bookedday.save()

    def test_endpoint(self):
        user = User.objects.create_superuser(
            "test", email="test@example.com", password="test"
        )
        self.client.login(username="test", password="test")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertCountEqual(response.json(), self.schedule_list)


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
