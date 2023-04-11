# Generated by Django 4.0.5 on 2022-10-17 18:58

from django.db import migrations, models
import django.db.models.deletion
import zebracrossing.campaigns.models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Campaign",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("client", models.CharField(max_length=200)),
                (
                    "ad_agency",
                    models.CharField(max_length=200, verbose_name="advertising agency"),
                ),
            ],
        ),
        migrations.CreateModel(
            name="TimeSlot",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("time", models.TimeField(verbose_name="Time")),
            ],
        ),
        migrations.CreateModel(
            name="Material",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "material",
                    models.FileField(
                        upload_to=zebracrossing.campaigns.models.Material.upload_to_campaign
                    ),
                ),
                (
                    "campaign",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="material",
                        to="campaigns.campaign",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="BookingSheet",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "ad_type",
                    models.CharField(
                        choices=[
                            ("SM", "Social Media"),
                            ("REC", "Recorded"),
                            ("LR", "Live Read"),
                            ("COMP", "Competition"),
                        ],
                        max_length=100,
                        verbose_name="type",
                    ),
                ),
                ("start_date", models.DateField(verbose_name="start date")),
                ("end_date", models.DateField(verbose_name="end date")),
                (
                    "booking_sheet",
                    models.FileField(
                        upload_to=zebracrossing.campaigns.models.BookingSheet.upload_to_campaign
                    ),
                ),
                ("cost", models.IntegerField()),
                (
                    "campaign",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="booking_sheets",
                        to="campaigns.campaign",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="BookedDay",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("date", models.DateField()),
                (
                    "bookingsheet",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="campaigns.bookingsheet",
                    ),
                ),
                (
                    "timeslot",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="campaigns.timeslot",
                    ),
                ),
            ],
        ),
    ]
