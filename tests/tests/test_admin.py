import unittest

from django.contrib.auth.models import User, Permission

from .base import TenantTestCase
from ..models import RestrictedModel


class TestAdmin(TenantTestCase):
    def user(self):
        user = User.objects.create_user(
            username='username',
            password='password',
            is_staff=True,
        )
        user.user_permissions.add(*Permission.objects.all())
        return user

    @unittest.expectedFailure
    def test_related_objects_only_show_from_active_tenant(self):
        a, b = self.build_tenants(2)

        RestrictedModel.objects.bulk_create([
            RestrictedModel(tenant=a, name='a'),
            RestrictedModel(tenant=b, name='b'),
            RestrictedModel(tenant=a, name='c'),
        ])
        user = self.user()
        user.visible_tenants.add(a, b)
        self.client.force_login(user)

        response = self.client.get('/admin/tests/restrictedmodel/')
        self.assertEqual(0, response.context['cl'].queryset.count())
