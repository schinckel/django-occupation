from django.test import TestCase

from occupation.utils import get_tenant_model

Tenant = get_tenant_model()


class TenantTestCase(TestCase):
    def build_tenants(self, count):
        tenants = [Tenant(name="{}".format(i)) for i in range(count)]
        Tenant.objects.bulk_create(tenants)
        return tenants
