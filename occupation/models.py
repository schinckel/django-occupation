from django.db import models
from django.utils.translation import ugettext as _
from django.conf import settings


class AbstractTenant(models.Model):
    tenant_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=256, unique=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        abstract = True

    def __str__(self):
        return '{name} ({pk})'.format(name=self.name, pk=self.pk)


class Tenant(AbstractTenant):
    users = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name='visible_tenants',
        help_text=_('Users that may access data from this tenant.')
    )

    class Meta:
        swappable = 'OCCUPATION_TENANT_MODEL'


class RLSTable(models.Model):
    pass
