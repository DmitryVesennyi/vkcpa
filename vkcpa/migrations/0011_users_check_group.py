# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vkcpa', '0010_auto_20161201_1440'),
    ]

    operations = [
        migrations.AddField(
            model_name='users',
            name='check_group',
            field=models.ManyToManyField(to='vkcpa.Groups'),
            preserve_default=True,
        ),
    ]
