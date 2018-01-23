# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vkcpa', '0005_auto_20161201_0637'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='groups',
            options={'ordering': ['behavior', 'sort_position'], 'verbose_name': '\u0421\u043f\u0438\u0441\u043e\u043a \u0432\u0441\u0435\u0445 \u0433\u0440\u0443\u043f\u043f', 'verbose_name_plural': '\u0421\u043f\u0438\u0441\u043e\u043a \u0432\u0441\u0435\u0445 \u0433\u0440\u0443\u043f\u043f'},
        ),
        migrations.AlterModelOptions(
            name='usergroup',
            options={'ordering': ['group_id'], 'verbose_name': '\u0413\u0440\u0443\u043f\u043f\u0430 \u043f\u043e\u043b\u044c\u0437\u043e\u0432\u0430\u0442\u0435\u043b\u044f', 'verbose_name_plural': '\u0413\u0440\u0443\u043f\u043f\u044b \u043f\u043e\u043b\u044c\u0437\u043e\u0432\u0430\u0442\u0435\u043b\u044f'},
        ),
        migrations.AlterModelOptions(
            name='users',
            options={'ordering': ['user_id'], 'verbose_name': '\u042e\u0437\u0435\u0440', 'verbose_name_plural': '\u042e\u0437\u0435\u0440\u044b'},
        ),
        migrations.AlterField(
            model_name='groups',
            name='sort_position',
            field=models.IntegerField(),
            preserve_default=True,
        ),
    ]
