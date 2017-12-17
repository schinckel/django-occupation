# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    run_before = [
        migrations.swappable_dependency(settings.OCCUPATION_TENANT_MODEL),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='Tenant',
            fields=[
                ('tenant_id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=256, unique=True)),
                ('is_active', models.BooleanField(default=True)),
                ('users', models.ManyToManyField(blank=True, help_text='Users that may access data from this tenant.', related_name='visible_tenants', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'swappable': 'OCCUPATION_TENANT_MODEL',
            },
        ),
    ]
