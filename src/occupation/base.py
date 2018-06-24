from django.conf import settings
from django.db import models


class BaseTenantModel(models.Model):
    tenant = models.ForeignKey(
        settings.OCCUPATION_TENANT_MODEL,
        related_name='+',
        on_delete=models.CASCADE
    )

    class Meta:
        abstract = True
