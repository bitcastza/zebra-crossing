# Generated by Django 3.0.3 on 2020-02-06 10:29

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('campaigns', '0009_auto_20200206_1221'),
    ]

    operations = [
        migrations.RenameField(
            model_name='material',
            old_name='booking_sheet',
            new_name='material',
        ),
    ]
