# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vkcpa', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='users',
            name='token',
            field=models.CharField(max_length=255, null=True, verbose_name='\u0422\u043e\u043a\u0435\u043d'),
            preserve_default=True,
        ),
    ]
