# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-05-15 16:33

import re

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('django_netjsonconfig', '0028_device_indexes'),
    ]

    operations = [
        migrations.AlterField(
            model_name='device',
            name='mac_address',
            field=models.CharField(db_index=True, help_text='primary mac address', max_length=17, unique=True, validators=[django.core.validators.RegexValidator(re.compile('^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})', 32), code='invalid', message='Must be a valid mac address.')]),
        ),
        migrations.AlterField(
            model_name='device',
            name='name',
            field=models.CharField(db_index=True, max_length=64, unique=True),
        ),
        migrations.AlterField(
            model_name='template',
            name='name',
            field=models.CharField(db_index=True, max_length=64, unique=True),
        ),
        migrations.AlterField(
            model_name='vpn',
            name='name',
            field=models.CharField(db_index=True, max_length=64, unique=True),
        ),
    ]
