# Generated by Django 2.2 on 2021-08-31 00:21

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('energy_metering', '0008_auto_20210831_0014'),
    ]

    operations = [
        migrations.RenameField(
            model_name='consumedenergy',
            old_name='mam_address',
            new_name='dlt_address',
        ),
        migrations.RenameField(
            model_name='generatedenergy',
            old_name='mam_address',
            new_name='dlt_address',
        ),
    ]