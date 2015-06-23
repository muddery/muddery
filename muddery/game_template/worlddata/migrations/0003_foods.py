# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('worlddata', '0002_auto_20150619_1724'),
    ]

    operations = [
        migrations.CreateModel(
            name='foods',
            fields=[
                ('key', models.CharField(max_length=255, serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('alias', models.CharField(max_length=255, blank=True)),
                ('typeclass', models.CharField(max_length=255)),
                ('desc', models.TextField(blank=True)),
                ('max_stack', models.IntegerField(default=1, blank=True)),
                ('unique', models.BooleanField()),
                ('lock', models.CharField(max_length=255, blank=True)),
                ('attributes', models.TextField(blank=True)),
                ('action', models.TextField(blank=True)),
                ('effect', models.TextField(blank=True)),
                ('effect_desc', models.TextField(blank=True)),
            ],
            options={
                'verbose_name': 'Food List',
                'verbose_name_plural': 'Food List',
            },
        ),
    ]
