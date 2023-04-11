from django.contrib import admin

from .models import Campaign, TimeSlot, BookingSheet, Material, BookedDay

admin.site.register(Campaign)
admin.site.register(TimeSlot)
admin.site.register(BookingSheet)
admin.site.register(Material)
admin.site.register(BookedDay)
