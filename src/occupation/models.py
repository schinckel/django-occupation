from django.conf import settings
from django.db import models
from django.utils.translation import ugettext as _


class AbstractTenant(models.Model):
    tenant_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=256, unique=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        abstract = True


class Tenant(AbstractTenant):
    users = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name='visible_tenants',
        help_text=_('Users that may access data from this tenant.')
    )

    class Meta:
        swappable = 'OCCUPATION_TENANT_MODEL'
