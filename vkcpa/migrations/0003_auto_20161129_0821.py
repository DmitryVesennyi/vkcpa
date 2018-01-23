# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vkcpa', '0002_users_token'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='users',
            name='hashmd5',
        ),
        migrations.AddField(
            model_name='users',
            name='expires_in',
            field=models.IntegerField(null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='users',
            name='name',
            field=models.CharField(max_length=255, verbose_name='\u0418\u043c\u044f', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='users',
            name='start_date',
            field=models.DateTimeField(auto_now=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='users',
            name='user_id',
            field=models.BigIntegerField(unique=True),
            preserve_default=True,
        ),
    ]
