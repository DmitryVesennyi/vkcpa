# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vkcpa', '0013_auto_20161215_1646'),
    ]

    operations = [
        migrations.AddField(
            model_name='users',
            name='check_group_static',
            field=models.ManyToManyField(to='vkcpa.StaticGroups'),
            preserve_default=True,
        ),
    ]
