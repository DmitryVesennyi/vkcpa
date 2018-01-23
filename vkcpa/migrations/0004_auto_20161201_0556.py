# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('vkcpa', '0003_auto_20161129_0821'),
    ]

    operations = [
        migrations.CreateModel(
            name='Groups',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('group_id', models.BigIntegerField(unique=True)),
                ('name', models.CharField(max_length=255, verbose_name='\u041d\u0430\u0437\u0432\u0430\u043d\u0438\u0435 \u0433\u0440\u0443\u043f\u043f\u044b', blank=True)),
                ('sort_position', models.IntegerField(unique=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='UserGroup',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('group_id', models.BigIntegerField(unique=True)),
                ('name', models.CharField(max_length=255, verbose_name='\u041d\u0430\u0437\u0432\u0430\u043d\u0438\u0435 \u0433\u0440\u0443\u043f\u043f\u044b', blank=True)),
                ('start_date', models.DateTimeField(auto_now_add=True)),
                ('groups', models.ManyToManyField(to='vkcpa.Groups', blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='users',
            name='user_group',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='vkcpa.UserGroup', null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='users',
            name='start_date',
            field=models.DateTimeField(),
            preserve_default=True,
        ),
    ]
