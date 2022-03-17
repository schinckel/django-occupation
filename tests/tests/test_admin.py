from django.contrib.auth.models import Permission, User

from occupation.utils import activate_tenant

from ..models import DistinctModel, RestrictedModel
from .base import TenantTestCase


class TestAdmin(TenantTestCase):
    def user(self):
        user = User.objects.create_user(
            username="username",
            password="password",
            is_staff=True,
        )
        user.user_permissions.add(*Permission.objects.all())
        return user

    def test_related_objects_only_show_from_active_tenant(self):
        a, b = self.build_tenants(2)

        activate_tenant(a.pk)

        RestrictedModel.objects.bulk_create(
            [
                RestrictedModel(tenant=a, name="a"),
                RestrictedModel(tenant=a, name="b"),
                RestrictedModel(tenant=a, name="c"),
            ]
        )

        activate_tenant(b.pk)

        RestrictedModel.objects.bulk_create(
            [
                RestrictedModel(tenant=b, name="d"),
                RestrictedModel(tenant=b, name="e"),
                RestrictedModel(tenant=b, name="f"),
            ]
        )

        activate_tenant("")

        user = self.user()
        user.visible_tenants.add(a, b)
        self.client.force_login(user)

        response = self.client.get("/admin/tests/restrictedmodel/")
        self.assertEqual(0, response.context["cl"].queryset.count())

        self.client.get("/__change_tenant__/{}/".format(a.pk))
        response = self.client.get("/admin/tests/restrictedmodel/")
        self.assertEqual(3, response.context["cl"].queryset.count())

    def test_tenant_field_is_hidden_in_admin(self):
        a, b = self.build_tenants(2)

        user = self.user()
        user.visible_tenants.add(a, b)
        self.client.force_login(user)

        self.client.get("/__change_tenant__/{}/".format(a.pk))
        response = self.client.get("/admin/tests/restrictedmodel/add/")
        self.assertTrue("tenant" not in response.context["adminform"].form.fields)

    def test_tenant_field_is_set_in_create(self):
        a, b = self.build_tenants(2)

        user = self.user()
        user.visible_tenants.add(a, b)
        self.client.force_login(user)

        self.client.get("/__change_tenant__/{}/".format(a.pk))
        self.client.post("/admin/tests/restrictedmodel/add/", {"name": "foo"})
        self.assertEqual(a, RestrictedModel.objects.get().tenant)

    def test_existing_object_cannot_be_moved(self):
        a, b = self.build_tenants(2)
        user = self.user()
        user.visible_tenants.add(a, b)

        activate_tenant(a.pk)
        obj = RestrictedModel.objects.create(tenant=a, name="b")

        self.client.force_login(user)

        # self.client.get('/__change_tenant__/{}/'.format(a.pk))
        self.client.post(
            "/admin/tests/restrictedmodel/{}/change/?__tenant={}".format(obj.pk, a.pk),
            {"name": "a"},
        )
        obj.refresh_from_db()
        self.assertEqual("a", obj.name)

    def test_distinct_models_are_not_affected(self):
        a, b = self.build_tenants(2)
        user = self.user()
        user.visible_tenants.add(a, b)

        self.client.force_login(user)
        self.client.post(
            "/admin/tests/distinctmodel/add/",
            {
                "name": "a",
            },
        )

        self.assertEqual(1, DistinctModel.objects.count())

    def test_tenant_selector_is_in_admin(self):
        a, b = self.build_tenants(2)
        user = self.user()
        user.visible_tenants.add(a, b)
        self.client.force_login(user)

        response = self.client.get("/admin/")
        self.assertTemplateUsed(response, "admin/change-tenant.html")
        self.assertTrue(b'select name="__tenant"' in response.content)
