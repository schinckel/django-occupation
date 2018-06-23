import unittest

from django.contrib.auth.models import User
from django.test import TestCase

from occupation.utils import get_tenant_model

Tenant = get_tenant_model()

CREDENTIALS = {
    'username': 'test',
    'password': 'test'
}


class TestMiddleware(TestCase):
    def build_tenants(self, count):
        tenants = [
            Tenant(name='{}'.format(i))
            for i in range(count)
        ]
        Tenant.objects.bulk_create(tenants)
        return tenants

    def test_view_without_tenant_aware_models_works_without_activation(self):
        response = self.client.get('/')
        self.assertEqual(200, response.status_code)
        self.assertEqual(b'None', response.content)

    def test_anonymous_user_may_not_change_tenant(self):
        a, _b = self.build_tenants(2)

        response = self.client.get('/', HTTP_X_CHANGE_TENANT=a.pk)
        self.assertEqual(403, response.status_code)

    @unittest.expectedFailure
    def test_only_one_available_tenant(self):
        a, _b = self.build_tenants(2)

        self.assertEqual(2, Tenant.objects.count())

        user = User.objects.create(**CREDENTIALS)
        user.visible_tenants.add(a)
        self.client.login(**CREDENTIALS)

        response = self.client.get('/')
        self.assertEqual('{}'.format(a.pk), response.content)
