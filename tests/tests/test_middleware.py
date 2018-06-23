from django.test import TestCase

from occupation.utils import get_tenant_model

Tenant = get_tenant_model()


class TestMiddleware(TestCase):
    def test_view_without_tenant_aware_models_works_without_activation(self):
        response = self.client.get('/')
        self.assertEqual(200, response.status_code)
        self.assertEqual(b'None', response.content)

    def test_anonymous_user_may_not_change_tenant(self):
        a, b = [Tenant(name='a'), Tenant(name='b')]
        Tenant.objects.bulk_create([a, b])

        response = self.client.get('/', HTTP_X_CHANGE_TENANT=a.pk)
        self.assertEqual(403, response.status_code)
