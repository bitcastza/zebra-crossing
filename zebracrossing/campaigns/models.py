from datetime import date

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

class TimeSlot(models.Model):
    time = models.TimeField(_('Time'))

    def __str__(self):
        return self.time.strftime("%H:%M")

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.time == other.time
        return False

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
    cost = models.IntegerField()

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

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            result = self.ad_type == other.ad_type and \
                    self.start_date == other.start_date and \
                    self.end_date == other.end_date and \
                    self.campaign == other.campaign and \
                    self.cost == other.cost
            return result
        return False

class Campaign(models.Model):
    client = models.CharField(max_length=200)
    ad_agency = models.CharField(_('advertising agency'), max_length=200)

    def __str__(self):
        return self.client + " from " + self.ad_agency

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.client == other.client and self.ad_agency == other.ad_agency
        return False;

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
            cost += booking.cost
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
