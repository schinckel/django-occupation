from typing import Optional, Sequence

from django.contrib import admin
from django.contrib.admin.models import LogEntry
from django.db import models
from django.db.models import Field, Model
from django.forms import Form
from django.http import HttpRequest

from occupation.models import Tenant
from occupation.utils import get_tenant_model


class TenantAdmin(admin.ModelAdmin):
    pass


if get_tenant_model() == Tenant:
    admin.site.register(Tenant, TenantAdmin)


def patch_admin() -> None:
    TenantModel = get_tenant_model()

    def get_tenant_field(model: type) -> Optional[Field]:
        for field in model._meta.fields:  # type: ignore
            if getattr(field, 'related_model', None) == TenantModel:
                return field
        return None

    class AutoTenantMixin:
        model: Model

        def get_fields(self, request: HttpRequest, obj: Model=None) -> Sequence[Field]:
            fields = super(AutoTenantMixin, self).get_fields(request, obj=obj)  # type: ignore
            tenant_field = get_tenant_field(self.model)
            if tenant_field and tenant_field.name in fields:
                fields.remove(tenant_field.name)
            return fields

    admin.ModelAdmin.__bases__ = (AutoTenantMixin,) + admin.ModelAdmin.__bases__

    def save_model(self, request: HttpRequest, obj: Model, form: Form, change: bool) -> None:
        if not change:
            tenant_field = get_tenant_field(obj)
            if tenant_field:
                setattr(obj, tenant_field.attname, request.session['active_tenant'])
        obj.save()

    admin.ModelAdmin.save_model = save_model

    if not getattr(LogEntry, 'tenant_id', None):
        # Adding this value is delegated to a postgres trigger - that way it will always
        # be set, without us having to query the database. We still need it as a field,
        # because it's tricky to .annotate() in the place where it's used. Otherwise,
        # we could write a cleaner version that just used default - however we can't do
        # that here because Django will send an explicit NULL, but we would want it not
        # to send it at all.
        LogEntry.add_to_class(
            'tenant_id',
            models.IntegerField(blank=True, null=True),
        )

    get_admin_url = admin.models.LogEntry.get_admin_url

    def get_admin_url_with_tenant(self):
        url = get_admin_url(self)
        if self.tenant_id and url:
            return '{0}?__tenant={1}'.format(url, self.tenant_id)
        return url

    admin.models.LogEntry.get_admin_url = get_admin_url_with_tenant
