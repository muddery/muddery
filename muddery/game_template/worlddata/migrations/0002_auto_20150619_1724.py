# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('worlddata', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='common_objects',
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
            ],
            options={
                'verbose_name': 'Common Object List',
                'verbose_name_plural': 'Common Object List',
            },
        ),
        migrations.CreateModel(
            name='object_creaters',
            fields=[
                ('key', models.CharField(max_length=255, serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('alias', models.CharField(max_length=255, blank=True)),
                ('typeclass', models.CharField(max_length=255)),
                ('desc', models.TextField(blank=True)),
                ('location', models.CharField(max_length=255, blank=True)),
                ('home', models.CharField(max_length=255, blank=True)),
                ('lock', models.CharField(max_length=255, blank=True)),
                ('attributes', models.TextField(blank=True)),
                ('obj_list', models.TextField(blank=True)),
                ('action', models.TextField(blank=True)),
            ],
            options={
                'verbose_name': 'World Object List',
                'verbose_name_plural': 'World Object List',
            },
        ),
        migrations.AddField(
            model_name='world_objects',
            name='action',
            field=models.TextField(blank=True),
        ),
    ]
