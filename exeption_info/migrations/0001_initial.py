# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='TracebagModel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('user_session', models.BigIntegerField(null=True, blank=True)),
                ('info', models.TextField(blank=True)),
            ],
            options={
                'ordering': ['date'],
                'db_table': '\u0422\u043e\u043b\u044c\u043a\u043e \u0434\u043b\u044f \u0441\u0443\u043f\u0435\u0440-\u0430\u0434\u043c\u0438\u043d\u043e\u0432',
                'verbose_name': '\u0422\u0440\u0435\u0439\u0441\u0431\u044d\u0433',
                'verbose_name_plural': '\u0422\u0440\u0435\u0439\u0441\u0431\u044d\u0433\u0438',
            },
            bases=(models.Model,),
        ),
    ]
