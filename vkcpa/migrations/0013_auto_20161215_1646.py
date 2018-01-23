# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vkcpa', '0012_auto_20161212_0659'),
    ]

    operations = [
        migrations.CreateModel(
            name='StaticGroups',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('group_id', models.BigIntegerField(unique=True)),
                ('link_group', models.URLField(null=True, blank=True)),
                ('name', models.CharField(max_length=255, null=True, verbose_name='\u041d\u0430\u0437\u0432\u0430\u043d\u0438\u0435 \u0433\u0440\u0443\u043f\u043f\u044b', blank=True)),
                ('start_date', models.DateTimeField(auto_now_add=True)),
                ('sort_position', models.IntegerField(null=True, blank=True)),
            ],
            options={
                'ordering': ['sort_position', 'start_date'],
                'db_table': '\u0421\u043f\u0438\u0441\u043e\u043a \u0441\u0442\u0430\u0442\u0438\u0447\u043d\u044b\u0445 \u0433\u0440\u0443\u043f\u043f',
                'verbose_name': '\u0421\u043f\u0438\u0441\u043e\u043a \u0441\u0442\u0430\u0442\u0438\u0447\u043d\u044b\u0445 \u0433\u0440\u0443\u043f\u043f',
                'verbose_name_plural': '\u0421\u043f\u0438\u0441\u043e\u043a \u0441\u0442\u0430\u0442\u0438\u0447\u043d\u044b\u0445 \u0433\u0440\u0443\u043f\u043f',
            },
            bases=(models.Model,),
        ),
        migrations.AlterModelOptions(
            name='groups',
            options={'ordering': ['behavior', 'sort_position', 'time'], 'verbose_name': '\u0421\u0442\u0435\u043a \u0433\u0440\u0443\u043f\u043f \u044e\u0437\u0435\u0440\u043e\u0432', 'verbose_name_plural': '\u0421\u0442\u0435\u043a \u0433\u0440\u0443\u043f\u043f \u044e\u0437\u0435\u0440\u043e\u0432'},
        ),
        migrations.AlterField(
            model_name='groups',
            name='behavior',
            field=models.IntegerField(default=1),
            preserve_default=True,
        ),
        migrations.AlterModelTable(
            name='groups',
            table='\u0421\u0442\u0435\u043a \u0433\u0440\u0443\u043f\u043f \u044e\u0437\u0435\u0440\u043e\u0432',
        ),
    ]
