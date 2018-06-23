from django.contrib.auth.models import User
from django.test import TestCase

from occupation.utils import get_tenant_model

Tenant = get_tenant_model()

CREDENTIALS = {
    'username': 'test',
    'password': 'test'
}


class TestContextProcessor(TestCase):
    def setUp(self):
        Tenant.objects.bulk_create([
            Tenant(name='a'),
            Tenant(name='b'),
            Tenant(name='c'),
        ])

    def test_no_tenant_if_anonymous(self):
        response = self.client.get('/change/')
        self.assertNotIn('visible_tenants', response.context)
        self.assertNotIn('active_tenant', response.context)
        self.assertNotIn('tenant_choices', response.context)

    def test_tenants_in_context(self):
        user = User.objects.create_user(**CREDENTIALS)
        tenants = Tenant.objects.exclude(name='b')
        user.visible_tenants.add(*tenants)
        self.client.login(**CREDENTIALS)
        resp = self.client.get('/change/')
        self.assertEqual(2, len(resp.context['visible_tenants']))
        self.assertIn(tenants[0], resp.context['visible_tenants'])
        self.assertIn(tenants[1], resp.context['visible_tenants'])
        self.assertEqual(None, resp.context['active_tenant'])

        resp = self.client.get('/change/', HTTP_X_CHANGE_TENANT=tenants[0].pk)
        self.assertEqual(2, len(resp.context['visible_tenants']))
        self.assertIn(tenants[0], resp.context['visible_tenants'])
        self.assertIn(tenants[1], resp.context['visible_tenants'])
        self.assertEqual(tenants[0].pk, resp.context['active_tenant'])

    def test_user_has_no_tenants(self):
        User.objects.create_user(**CREDENTIALS)
        self.client.login(**CREDENTIALS)
        resp = self.client.get('/change/')
        self.assertEqual([], list(resp.context['visible_tenants']))
        self.assertEqual([], list(resp.context['tenant_choices']))
