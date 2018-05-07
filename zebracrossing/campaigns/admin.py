from django.contrib import admin

from .models import Campaign, TimeSlot, BookingSheet

admin.site.register(Campaign)
admin.site.register(TimeSlot)
admin.site.register(BookingSheet)
