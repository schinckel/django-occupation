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

    # get_admin_url = admin.models.LogEntry.get_admin_url
    #
    # def get_admin_url_with_tenant(self):
    #     url = get_admin_url(self)
    #
    #     # Okay, we can't do this just yet because it will hit the database, and get
    #     # an exception that it's not found (because this session may not be able to
    #     # view it), and render as a deleted object.
    #
    #     # Our other alternative is to do what we did in django-boardinghouse and
    #     # save that as an extra field.
    #     instance = self.get_edited_object()
    #     tenant_field = get_tenant_field(instance)
    #     if tenant_field:
    #         tenant_id = getattr(instance, tenant_field.attname)
    #         if '?' in url:
    #             url += '&__tenant={}'.format(tenant_id)
    #         else:
    #             url += '?__tenant={}'.format(tenant_id)
    #
    #     return url
    #
    # admin.models.LogEntry.get_admin_url = get_admin_url_with_tenant
