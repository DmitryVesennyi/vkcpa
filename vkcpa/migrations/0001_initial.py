# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Users',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('user_id', models.BigIntegerField()),
                ('name', models.CharField(max_length=255, verbose_name='\u0418\u043c\u044f')),
                ('surname', models.CharField(max_length=255, verbose_name='\u0424\u0430\u043c\u0438\u043b\u0438\u044f', blank=True)),
                ('start_date', models.DateTimeField(auto_now_add=True)),
                ('hashmd5', models.CharField(max_length=255, verbose_name='\u0425\u0435\u0448')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
