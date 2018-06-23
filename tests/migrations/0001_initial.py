# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AwareModel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=10)),
                ('status', models.BooleanField(default=False)),
                ('factor', models.PositiveSmallIntegerField(default=7)),
                ('tenant', models.ForeignKey(on_delete=models.CASCADE, to='occupation.Tenant')),
            ],
        ),
        migrations.CreateModel(
            name='CoReferentialModelA',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=10)),
            ],
        ),
        migrations.CreateModel(
            name='CoReferentialModelB',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=10)),
                ('other', models.ForeignKey(on_delete=models.CASCADE, related_name='model_b', blank=True, to='tests.CoReferentialModelA', null=True)),
            ],
        ),
        migrations.CreateModel(
            name='NaiveModel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=10)),
                ('status', models.BooleanField(default=False)),
            ],
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SelfReferentialModel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=10)),
                ('parent', models.ForeignKey(on_delete=models.CASCADE, related_name='children', blank=True, to='tests.SelfReferentialModel', null=True)),
            ],
        ),
        migrations.AddField(
            model_name='coreferentialmodela',
            name='other',
            field=models.ForeignKey(on_delete=models.CASCADE, related_name='model_a', blank=True, to='tests.CoReferentialModelB', null=True),
        ),
        migrations.CreateModel(
            name='ModelA',
            fields=[
                ('id', models.AutoField())
            ],
            bases=(models.Model,)
        ),
        migrations.CreateModel(
            name='ModelB',
            fields=[
                ('id', models.AutoField())
            ],
            bases=(models.Model,)
        ),
        migrations.CreateModel(
            name='ModelBPrefix',
            fields=[
                ('id', models.AutoField())
            ],
            bases=(models.Model,)
        ),
        migrations.AddField(
            model_name='modelbprefix',
            name='a',
            field=models.ForeignKey(on_delete=models.CASCADE, related_name='model_b', blank=True, to='tests.ModelA', null=True),
        ),
        migrations.CreateModel(
            name='SettingsSharedModel',
            fields=[
                ('id', models.AutoField())
            ],
            bases=(models.Model,)
        ),
        migrations.CreateModel(
            name='SettingsPrivateModel',
            fields=[
                ('id', models.AutoField())
            ],
            bases=(models.Model,)
        ),
        migrations.CreateModel(
            name='ViewBackedModel',
            fields=[
                ('id', models.AutoField())
            ],
            bases=(models.Model,),
            options={'managed': False},
        ),
        migrations.RunSQL(
            sql='CREATE VIEW tests_viewbackedmodel AS (SELECT x AS id FROM generate_series(1, 1000) x)',
            reverse_sql='DROP VIEW tests_viewbackedmodel'
        )
    ]
