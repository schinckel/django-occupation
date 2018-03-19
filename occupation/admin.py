from django.contrib import admin

from .models import Tenant
from .utils import get_tenant_model


class TenantAdmin(admin.ModelAdmin):
    pass


if get_tenant_model() == Tenant:
    admin.site.register(Tenant, TenantAdmin)


def patch_admin():
    TenantModel = get_tenant_model()

    def get_tenant_field(model):
        for field in model._meta.fields:
            if getattr(field, 'related_model', None) == TenantModel:
                return field

    class AutoTenantMixin(object):
        def get_fields(self, request, obj=None):
            fields = super(AutoTenantMixin, self).get_fields(request, obj=obj)
            tenant_field = get_tenant_field(self.model)
            if tenant_field and tenant_field.name in fields:
                fields.remove(tenant_field.name)
            return fields

    admin.ModelAdmin.__bases__ = (AutoTenantMixin,) + admin.ModelAdmin.__bases__

    def save_model(self, request, obj, form, change):
        if not change:
            tenant_field = get_tenant_field(obj)
            if tenant_field:
                setattr(obj, tenant_field.attname, request.session['active_tenant'])
        obj.save()

    admin.ModelAdmin.save_model = save_model
