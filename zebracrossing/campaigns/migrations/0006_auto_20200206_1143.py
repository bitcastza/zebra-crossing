# Generated by Django 3.0.3 on 2020-02-06 09:43

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("campaigns", "0005_remove_bookingsheet_time_slots"),
    ]

    operations = [
        migrations.RenameField(
            model_name="bookingsheet",
            old_name="material",
            new_name="booking_sheet",
        ),
    ]