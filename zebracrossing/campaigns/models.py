from datetime import date

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

class TimeSlot(models.Model):
    start_time = models.TimeField(_('start time'))
    end_time = models.TimeField(_('end time'))

    def __str__(self):
        return self.start_time.strftime("%H:%M") + " - " + self.end_time.strftime("%H:%M")

class BookingSheet(models.Model):
    def upload_to_campaign(instance, filename):
        return "campaigns/{0}/bookings/{1}".format(instance.campaign.id, filename)

    AD_TYPES = (
        ('SM', 'Social Media'),
        ('REC', 'Recorded'),
        ('LR', 'Live Read'),
        ('COMP', 'Competition')
    )
    ad_type = models.CharField(_('type'), max_length=100, choices=AD_TYPES)
    start_date = models.DateField(_('start date'))
    end_date = models.DateField(_('end date'))
    campaign = models.ForeignKey('Campaign', on_delete=models.CASCADE)
    material = models.FileField(upload_to=upload_to_campaign)

    def clean_fields(self, exclude=None):
        super().clean_fields(exclude=exclude)
        if self.start_date > self.end_date:
            if exclude and 'start_date' in exclude:
                raise ValidationError(_("Start date is after end date"))
            else:
                raise ValidationError({'start_date': _("Start date is after end date")})
        if self.campaign is None:
            raise ValidationError(_("Campaign not specified"))

    def __str__(self):
        return self.campaign.get_client() + " (" + \
                self.campaign.get_ad_agency() + "): " + \
                self.start_date.strftime("%Y/%m/%d") + " - " + \
                self.end_date.strftime("%Y/%m/%d") + " (" + self.ad_type + ")"

class Campaign(models.Model):
    client = models.CharField(max_length=200)
    ad_agency = models.CharField(_('advertising agency'), max_length=200)

    def __str__(self):
        return self.client + " from " + self.ad_agency

    def get_client(self):
        return self.client

    def get_ad_agency(self):
        return self.ad_agency

    def get_start_date(self):
        booking_sheets = BookingSheet.objects.filter(campaign=self.id)
        if len(booking_sheets) == 0:
            return None
        start_date = date.max
        for sheet in booking_sheets:
            if sheet.start_date < start_date:
                start_date = sheet.start_date
        return start_date

    def get_end_date(self):
        booking_sheets = BookingSheet.objects.filter(campaign=self.id)
        if len(booking_sheets) == 0:
            return None
        end_date = date.min
        for sheet in booking_sheets:
            if sheet.end_date > end_date:
                end_date = sheet.end_date
        return end_date

    def get_cost(self):
        cost = 0
        booking_sheets = BookingSheet.objects.filter(campaign=self.id)
        for booking in booking_sheets:
            time_slots = CampaignBookingCost.objects.filter(booking_sheet=booking.id)
            for slot in time_slots:
                cost += slot.cost
        return cost

    def get_booking_sheets(self):
        return BookingSheet.objects.filter(campaign=self.id)

    def is_active(self):
        today = date.today()
        start_date = self.get_start_date()
        end_date = self.get_end_date()
        if start_date == None or end_date == None:
            return False
        return start_date <= today and end_date >= today

class CampaignBookingCost(models.Model):
    class Meta:
        unique_together = (('time_slot', 'booking_sheet'),)

    time_slot = models.ForeignKey(TimeSlot, on_delete=models.CASCADE)
    booking_sheet = models.ForeignKey(BookingSheet, on_delete=models.CASCADE)
    cost = models.IntegerField()

    def __str__(self):
        time_slot = TimeSlot.objects.get(id=self.time_slot)
        booking_sheet = BookingSheet.objects.get(id=self.booking_sheet)
        return booking_sheet + ": " + booking_sheet + " (R" + self.cost + ")"
