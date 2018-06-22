import unittest

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.test import TestCase, modify_settings

from occupation.utils import get_tenant_model


class TestSwappableModel(TestCase):
    @modify_settings()
    def test_schema_model_app_not_found(self):
        settings.OCCUPATION_TENANT_MODEL = 'foo.bar'
        with self.assertRaises(ImproperlyConfigured):
            get_tenant_model()

    @modify_settings()
    def test_schema_model_model_not_found(self):
        settings.OCCUPATION_TENANT_MODEL = 'occupation.NotSchemaModel'
        with self.assertRaises(ImproperlyConfigured):
            get_tenant_model()

    @modify_settings()
    def test_invalid_schema_model_string(self):
        settings.OCCUPATION_TENANT_MODEL = 'foo__bar'
        with self.assertRaises(ImproperlyConfigured):
            get_tenant_model()

    @unittest.expectedFailure
    @modify_settings()
    def test_swappable_model_changes_schema_template_verbose_names(self):
        settings.OCCUPATION_TENANT_MODEL = 'tests.NaiveModel'
        from occupation.contrib.template.models import TenantTemplate
        self.assertEqual('template naive model', str(TenantTemplate._meta.verbose_name))
        self.assertEqual('template naive models', str(TenantTemplate._meta.verbose_name_plural))
