# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-06-28 14:48
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kofan', '0003_user_icon'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='icon',
            field=models.ImageField(default='upload/default.jpg', upload_to='upload'),
        ),
    ]
