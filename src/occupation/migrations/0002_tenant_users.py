# Generated by Django 2.0 on 2017-12-18 08:51

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("occupation", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="tenant",
            name="users",
            field=models.ManyToManyField(
                blank=True,
                help_text="Users that may access data from this tenant.",
                related_name="visible_tenants",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
