# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='dialogues',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('dialogue', models.CharField(max_length=255)),
                ('sentence', models.IntegerField()),
                ('speaker', models.CharField(max_length=255, blank=True)),
                ('content', models.TextField(blank=True)),
                ('next', models.CharField(max_length=255, blank=True)),
                ('condition', models.TextField(blank=True)),
                ('action', models.TextField(blank=True)),
            ],
            options={
                'verbose_name': 'World Dialogue List',
                'verbose_name_plural': 'World Dialogue List',
            },
        ),
        migrations.CreateModel(
            name='personal_objects',
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
            ],
            options={
                'verbose_name': 'Personal Object List',
                'verbose_name_plural': 'Personal Object List',
            },
        ),
        migrations.CreateModel(
            name='world_details',
            fields=[
                ('key', models.CharField(max_length=255, serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('desc', models.TextField(blank=True)),
                ('location', models.CharField(max_length=255, blank=True)),
            ],
            options={
                'verbose_name': 'World Detail List',
                'verbose_name_plural': 'World Detail List',
            },
        ),
        migrations.CreateModel(
            name='world_exits',
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
                ('destination', models.CharField(max_length=255, blank=True)),
            ],
            options={
                'verbose_name': 'World Exit List',
                'verbose_name_plural': 'World Exit List',
            },
        ),
        migrations.CreateModel(
            name='world_npcs',
            fields=[
                ('key', models.CharField(max_length=255, serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('alias', models.CharField(max_length=255, blank=True)),
                ('typeclass', models.CharField(max_length=255)),
                ('desc', models.TextField(blank=True)),
                ('location', models.CharField(max_length=255, blank=True)),
                ('home', models.CharField(max_length=255, blank=True)),
                ('dialogue', models.CharField(max_length=255, blank=True)),
                ('lock', models.CharField(max_length=255, blank=True)),
                ('attributes', models.TextField(blank=True)),
            ],
            options={
                'verbose_name': 'World NPC List',
                'verbose_name_plural': 'World NPC List',
            },
        ),
        migrations.CreateModel(
            name='world_objects',
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
            ],
            options={
                'verbose_name': 'World Object List',
                'verbose_name_plural': 'World Object List',
            },
        ),
        migrations.CreateModel(
            name='world_rooms',
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
            ],
            options={
                'verbose_name': 'World Room List',
                'verbose_name_plural': 'World Room List',
            },
        ),
    ]
