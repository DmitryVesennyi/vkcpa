# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('vkcpa', '0011_users_check_group'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='groups',
            options={'ordering': ['behavior', 'sort_position', 'time'], 'verbose_name': '\u0421\u043f\u0438\u0441\u043e\u043a \u0432\u0441\u0435\u0445 \u0433\u0440\u0443\u043f\u043f', 'verbose_name_plural': '\u0421\u043f\u0438\u0441\u043e\u043a \u0432\u0441\u0435\u0445 \u0433\u0440\u0443\u043f\u043f'},
        ),
        migrations.RenameField(
            model_name='users',
            old_name='banan',
            new_name='ban',
        ),
        migrations.RenameField(
            model_name='users',
            old_name='referalls',
            new_name='referals',
        ),
        migrations.RemoveField(
            model_name='groups',
            name='group_id',
        ),
        migrations.RemoveField(
            model_name='groups',
            name='name',
        ),
        migrations.RemoveField(
            model_name='usergroup',
            name='groups',
        ),
        migrations.AddField(
            model_name='groups',
            name='group_info',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='vkcpa.UserGroup', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='groups',
            name='time',
            field=models.DateTimeField(default=datetime.datetime(2016, 12, 12, 6, 59, 1, 488808), auto_now=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='usergroup',
            name='banan',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='usergroup',
            name='link_group',
            field=models.URLField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='usergroup',
            name='queue',
            field=models.IntegerField(default=0, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='users',
            name='count',
            field=models.IntegerField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='users',
            name='photo',
            field=models.URLField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='users',
            name='who_invited',
            field=models.BigIntegerField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='users',
            name='name',
            field=models.CharField(max_length=255, null=True, verbose_name='\u0418\u043c\u044f', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='users',
            name='surname',
            field=models.CharField(max_length=255, null=True, verbose_name='\u0424\u0430\u043c\u0438\u043b\u0438\u044f', blank=True),
            preserve_default=True,
        ),
    ]
