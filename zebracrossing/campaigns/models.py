from datetime import date
from pathlib import Path

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _


class TimeSlot(models.Model):
    time = models.TimeField(_("Time"))

    def __str__(self):
        return self.time.strftime("%H:%M")

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.time == other.time
        return False


class BookedDay(models.Model):
    date = models.DateField()
    timeslot = models.ForeignKey("TimeSlot", on_delete=models.CASCADE)
    bookingsheet = models.ForeignKey("BookingSheet", on_delete=models.CASCADE)

    def __str__(self):
        return (
            self.date.strftime("%Y-%m-%d")
            + " "
            + str(self.timeslot)
            + " "
            + str(self.bookingsheet)
        )


class BookingSheet(models.Model):
    def upload_to_campaign(instance, filename):
        return f"campaigns/{instance.campaign.id}/bookings/{filename}"

    AD_TYPES = (
        ("SM", "Social Media"),
        ("REC", "Recorded"),
        ("LR", "Live Read"),
        ("COMP", "Competition"),
    )
    ad_type = models.CharField(_("type"), max_length=100, choices=AD_TYPES)
    start_date = models.DateField(_("start date"))
    end_date = models.DateField(_("end date"))
    campaign = models.ForeignKey(
        "Campaign", on_delete=models.CASCADE, related_name="booking_sheets"
    )
    booking_sheet = models.FileField(upload_to=upload_to_campaign)
    cost = models.IntegerField()

    def clean_fields(self, exclude=None):
        super().clean_fields(exclude=exclude)
        if self.start_date > self.end_date:
            if exclude and "start_date" in exclude:
                raise ValidationError(_("Start date is after end date"))
            else:
                raise ValidationError({"start_date": _("Start date is after end date")})
        if self.campaign is None:
            raise ValidationError(_("Campaign not specified"))

    def __str__(self):
        return (
            self.campaign.client
            + " ("
            + self.campaign.ad_agency
            + "): "
            + self.start_date.strftime("%Y/%m/%d")
            + " - "
            + self.end_date.strftime("%Y/%m/%d")
            + " ("
            + self.ad_type
            + ")"
        )

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            result = (
                self.ad_type == other.ad_type
                and self.start_date == other.start_date
                and self.end_date == other.end_date
                and self.campaign == other.campaign
                and self.cost == other.cost
            )
            return result
        return False


class Campaign(models.Model):
    client = models.CharField(max_length=200)
    ad_agency = models.CharField(_("advertising agency"), max_length=200)

    def __str__(self):
        return self.client + " from " + self.ad_agency

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.client == other.client and self.ad_agency == other.ad_agency
        return False

    @property
    def start_date(self):
        booking_sheets = self.booking_sheets.all()
        if len(booking_sheets) == 0:
            return None
        start_date = date.max
        for sheet in booking_sheets:
            if sheet.start_date < start_date:
                start_date = sheet.start_date
        return start_date

    @property
    def end_date(self):
        booking_sheets = self.booking_sheets.all()
        if len(booking_sheets) == 0:
            return None
        end_date = date.min
        for sheet in booking_sheets:
            if sheet.end_date > end_date:
                end_date = sheet.end_date
        return end_date

    @property
    def cost(self):
        cost = 0
        for booking in self.booking_sheets.all():
            cost += booking.cost
        return cost

    def is_active(self):
        today = date.today()
        start_date = self.start_date
        end_date = self.end_date
        if start_date is None or end_date is None:
            return False
        return start_date <= today and end_date >= today


class Material(models.Model):
    def upload_to_campaign(instance, filename):
        return f"campaigns/{instance.campaign.id}/material/{filename}"

    campaign = models.ForeignKey(
        Campaign, on_delete=models.CASCADE, related_name="material"
    )
    material = models.FileField(upload_to=upload_to_campaign)

    def __str__(self):
        p = Path(self.material.name)
        return f"{p.name}"
