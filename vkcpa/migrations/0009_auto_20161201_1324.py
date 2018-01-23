# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vkcpa', '0008_auto_20161201_1153'),
    ]

    operations = [
        migrations.AddField(
            model_name='users',
            name='referalls',
            field=models.CharField(max_length=255, null=True, verbose_name='\u0420\u0435\u0444\u0435\u0440\u0430\u043b\u044c\u043d\u0430\u044f \u0441\u0441\u044b\u043b\u043a\u0430'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='groups',
            name='name',
            field=models.CharField(max_length=255, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='usergroup',
            name='name',
            field=models.CharField(max_length=255, null=True, verbose_name='\u041d\u0430\u0437\u0432\u0430\u043d\u0438\u0435 \u0433\u0440\u0443\u043f\u043f\u044b', blank=True),
            preserve_default=True,
        ),
    ]
