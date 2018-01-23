# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vkcpa', '0006_auto_20161201_0806'),
    ]

    operations = [
        migrations.AlterField(
            model_name='groups',
            name='sort_position',
            field=models.IntegerField(blank=True),
            preserve_default=True,
        ),
    ]
