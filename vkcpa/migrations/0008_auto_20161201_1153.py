# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vkcpa', '0007_auto_20161201_0835'),
    ]

    operations = [
        migrations.AlterField(
            model_name='groups',
            name='name',
            field=models.CharField(max_length=255, null=True, verbose_name='\u041d\u0430\u0437\u0432\u0430\u043d\u0438\u0435 \u0433\u0440\u0443\u043f\u043f\u044b', blank=True),
            preserve_default=True,
        ),
    ]
