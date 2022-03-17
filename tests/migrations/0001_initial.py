# -*- coding: utf-8 -*-
from typing import List, Tuple

from django.db import migrations, models

import occupation.operations


class Migration(migrations.Migration):

    dependencies: List[Tuple[str, str]] = []

    operations = [
        migrations.CreateModel(
            name="RelatedModel",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                ("name", models.CharField(unique=True, max_length=10)),
                ("status", models.BooleanField(default=False)),
                ("factor", models.PositiveSmallIntegerField(default=7)),
                (
                    "tenant",
                    models.ForeignKey(on_delete=models.CASCADE, to="occupation.Tenant"),
                ),
            ],
        ),
        migrations.CreateModel(
            name="RestrictedModel",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                ("name", models.CharField(unique=True, max_length=10)),
                (
                    "tenant",
                    models.ForeignKey(on_delete=models.CASCADE, to="occupation.Tenant"),
                ),
            ],
        ),
        occupation.operations.EnableRowLevelSecurity("RestrictedModel"),
        migrations.CreateModel(
            name="DistinctModel",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                ("name", models.CharField(unique=True, max_length=10)),
                ("status", models.BooleanField(default=False)),
            ],
            bases=(models.Model,),
        ),
    ]
