# Generated by Django 3.0.3 on 2020-02-06 09:55

from django.db import migrations, models
import django.db.models.deletion
import zebracrossing.campaigns.models


class Migration(migrations.Migration):

    dependencies = [
        ('campaigns', '0006_auto_20200206_1143'),
    ]

    operations = [
        migrations.CreateModel(
            name='Material',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('booking_sheet', models.FileField(upload_to=zebracrossing.campaigns.models.Material.upload_to_campaign)),
                ('campaign', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='campaigns.Campaign')),
            ],
        ),
    ]
