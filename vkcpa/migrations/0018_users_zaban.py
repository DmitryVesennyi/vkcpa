# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vkcpa', '0017_auto_20170210_1324'),
    ]

    operations = [
        migrations.AddField(
            model_name='users',
            name='zaban',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]
