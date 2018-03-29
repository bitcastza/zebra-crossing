from django.contrib import admin

from .models import Campaign, TimeSlot, BookingSheet, CampaignBookingCost

admin.site.register(Campaign)
admin.site.register(TimeSlot)
admin.site.register(BookingSheet)
admin.site.register(CampaignBookingCost)
