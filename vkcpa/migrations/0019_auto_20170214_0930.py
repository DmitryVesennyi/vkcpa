# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('vkcpa', '0018_users_zaban'),
    ]

    operations = [
        migrations.AddField(
            model_name='staticgroups',
            name='end_limit',
            field=models.DateTimeField(default=datetime.datetime(2017, 2, 14, 9, 29, 30, 666708), auto_now=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='staticgroups',
            name='impression',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='staticgroups',
            name='limit_impressions',
            field=models.IntegerField(default=100),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='usergroup',
            name='end_limit',
            field=models.DateTimeField(default=datetime.datetime(2017, 2, 14, 9, 30, 39, 935994), auto_now=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='usergroup',
            name='impression',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='usergroup',
            name='limit_impressions',
            field=models.IntegerField(default=100),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='usergroup',
            name='queue',
            field=models.IntegerField(default=0, null=True, verbose_name='\u0417\u0430\u043f\u0430\u0441 \u043a\u0440\u0443\u0433\u043e\u0432', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='users',
            name='who_invited',
            field=models.BigIntegerField(null=True, blank=True),
            preserve_default=True,
        ),
    ]
