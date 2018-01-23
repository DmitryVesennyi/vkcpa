# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vkcpa', '0014_users_check_group_static'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='staticgroups',
            options={'ordering': ['sort_position', 'start_date'], 'verbose_name': '\u0421\u043f\u0438\u0441\u043e\u043a \u0441\u0442\u0430\u0442\u0438\u0447\u043d\u044b\u0445 \u0433\u0440\u0443\u043f\u043f', 'verbose_name_plural': '\u0421\u043f\u0438\u0441\u043e\u043a \u0441\u0442\u0430\u0442\u0438\u0447\u043d\u044b\u0445 \u0433\u0440\u0443\u043f\u043f \u0440\u0435\u0441\u0443\u0440\u0441\u0430'},
        ),
        migrations.AlterModelOptions(
            name='usergroup',
            options={'ordering': ['group_id'], 'verbose_name': '\u0413\u0440\u0443\u043f\u043f\u0430 \u043f\u043e\u043b\u044c\u0437\u043e\u0432\u0430\u0442\u0435\u043b\u044f', 'verbose_name_plural': '\u0413\u0440\u0443\u043f\u043f\u044b \u043f\u043e\u043b\u044c\u0437\u043e\u0432\u0430\u0442\u0435\u043b\u0435\u0439'},
        ),
    ]
