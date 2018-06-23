# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='RelatedModel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=10)),
                ('status', models.BooleanField(default=False)),
                ('factor', models.PositiveSmallIntegerField(default=7)),
                ('tenant', models.ForeignKey(on_delete=models.CASCADE, to='occupation.Tenant')),
            ],
        ),
        migrations.CreateModel(
            name='DistinctModel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=10)),
                ('status', models.BooleanField(default=False)),
            ],
            bases=(models.Model,),
        ),
    ]
