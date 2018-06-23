import unittest

from django.contrib.auth.models import User

from .base import TenantTestCase, Tenant


CREDENTIALS = {
    'username': 'test',
    'password': 'test'
}

SU_CREDENTIALS = {
    'username': 'su',
    'password': 'su',
}


class TestMiddleware(TenantTestCase):
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
        self.client.force_login(user)

        response = self.client.get('/')
        self.assertEqual('{}'.format(a.pk), response.content)

    def test_middleware_activation_on_get(self):
        a, b = self.build_tenants(2)

        user = User.objects.create(**CREDENTIALS)
        user.visible_tenants.add(a, b)
        self.client.force_login(user)

        self.client.get('/__change_tenant__/{}/'.format(b.pk))
        response = self.client.get('/')
        self.assertEqual(b.pk, int(response.content))

        response = self.client.get('/', {'__tenant': a.pk}, follow=True)
        self.assertEqual(a.pk, int(response.content))

        response = self.client.get('/', {'__tenant': b.pk, 'foo': 'bar'}, follow=True)
        self.assertEqual(b.pk, self.client.session['active_tenant'])
        self.assertEqual(b'foo=bar', response.content.split(b'\n')[1])

        response = self.client.get('/', HTTP_X_CHANGE_TENANT=a.pk)
        self.assertEqual(a.pk, int(response.content))

    def test_middleware_activation_on_post(self):
        a, b = self.build_tenants(2)

        user = User.objects.create(**CREDENTIALS)
        user.visible_tenants.add(a, b)
        self.client.force_login(user)

        response = self.client.post('/__change_tenant__/{}/'.format(b.pk))
        self.assertEqual(b.pk, self.client.session['active_tenant'])

        response = self.client.post('/?__tenant={}'.format(a.pk), follow=True)
        self.assertEqual(a.pk, self.client.session['active_tenant'])

        response = self.client.post('/?__tenant={}&foo=bar'.format(b.pk), follow=True)
        self.assertEqual(b.pk, self.client.session['active_tenant'])
        tenant, query = response.content.split(b'\n')
        self.assertEqual(b.pk, int(tenant))
        self.assertEqual(b'foo=bar', query)

        response = self.client.post('/', HTTP_X_CHANGE_TENANT=a.pk)
        self.assertEqual(a.pk, int(response.content))

    def test_forbidden_tenant(self):
        a, b, c = self.build_tenants(3)
        user = User.objects.create(**CREDENTIALS)
        self.client.force_login(user)

        response = self.client.get('/', {'__tenant': a.pk}, follow=True)
        self.assertEqual(403, response.status_code)

        user.visible_tenants.add(a)
        response = self.client.get('/', {'__tenant': a.pk}, follow=True)
        self.assertEqual(200, response.status_code)
        self.assertEqual(a.pk, int(response.content))

    def test_deactivate_tenant(self):
        a = self.build_tenants(1)[0]
        user = User.objects.create(**CREDENTIALS)
        user.visible_tenants.add(a)
        self.client.force_login(user)

        self.client.get('/__change_tenant__/{}/'.format(a.pk))
        self.assertEqual(a.pk, self.client.session['active_tenant'])
        self.client.get('/__change_tenant__//')
        self.assertFalse('active_tenant' in self.client.session)

    def test_tenant_is_already_active_does_not_hit_database(self):
        a, b = self.build_tenants(2)

        user = User.objects.create(**CREDENTIALS)
        user.visible_tenants.add(a, b)
        self.client.force_login(user)

        self.client.get('/__change_tenant__/{}/'.format(a.pk))
        self.assertEqual(a.pk, self.client.session['active_tenant'])

        with self.assertNumQueries(1):
            self.client.get('/__change_tenant__/{}/'.format(a.pk))
