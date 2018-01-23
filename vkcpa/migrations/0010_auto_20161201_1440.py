# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vkcpa', '0009_auto_20161201_1324'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='groups',
            options={'ordering': ['behavior', '-pk'], 'verbose_name': '\u0421\u043f\u0438\u0441\u043e\u043a \u0432\u0441\u0435\u0445 \u0433\u0440\u0443\u043f\u043f', 'verbose_name_plural': '\u0421\u043f\u0438\u0441\u043e\u043a \u0432\u0441\u0435\u0445 \u0433\u0440\u0443\u043f\u043f'},
        ),
        migrations.AlterField(
            model_name='groups',
            name='sort_position',
            field=models.IntegerField(null=True, blank=True),
            preserve_default=True,
        ),
    ]
