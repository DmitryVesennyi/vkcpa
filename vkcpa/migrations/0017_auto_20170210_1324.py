# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vkcpa', '0016_usergroup_count'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='groups',
            options={'ordering': ['behavior', 'sort_position', 'time'], 'verbose_name': '\u0421\u043f\u0438\u0441\u043e\u043a', 'verbose_name_plural': '\u0421\u043f\u0438\u0441\u043e\u043a'},
        ),
        migrations.AlterModelOptions(
            name='staticgroups',
            options={'ordering': ['sort_position', 'start_date'], 'verbose_name': '\u041f\u0430\u0440\u0442\u043d\u0435\u0440', 'verbose_name_plural': '\u041f\u0430\u0440\u0442\u043d\u0435\u0440\u044b'},
        ),
        migrations.AlterModelOptions(
            name='usergroup',
            options={'ordering': ['group_id'], 'verbose_name': '\u0413\u0440\u0443\u043f\u043f\u0430', 'verbose_name_plural': '\u0413\u0440\u0443\u043f\u043f\u044b'},
        ),
        migrations.AlterField(
            model_name='usergroup',
            name='count',
            field=models.IntegerField(default=0, null=True, verbose_name='\u041f\u0440\u0438\u0433\u043b\u0430\u0441\u0438\u043b', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='usergroup',
            name='queue',
            field=models.IntegerField(default=0, null=True, verbose_name='\u041a\u0440\u0443\u0433\u043e\u0432', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='users',
            name='ban',
            field=models.IntegerField(default=0),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='users',
            name='count',
            field=models.IntegerField(null=True, verbose_name='\u041a\u043e\u043b\u0438\u0447\u0435\u0441\u0442\u0432\u043e \u043f\u0440\u0438\u0433\u043b\u0430\u0448\u0435\u043d\u043d\u044b\u0445', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='users',
            name='who_invited',
            field=models.BigIntegerField(null=True, verbose_name='\u041a\u0442\u043e \u043f\u0440\u0438\u0433\u043b\u0430\u0441\u0438\u043b', blank=True),
            preserve_default=True,
        ),
    ]
