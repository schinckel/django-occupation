from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.test import TestCase, modify_settings
from django.utils import six

from boardinghouse.schema import get_schema_model


class TestSwappableModel(TestCase):

    @modify_settings()
    def test_schema_model_app_not_found(self):
        settings.BOARDINGHOUSE_SCHEMA_MODEL = 'foo.bar'
        with self.assertRaises(ImproperlyConfigured):
            get_schema_model()

    @modify_settings()
    def test_schema_model_model_not_found(self):
        settings.BOARDINGHOUSE_SCHEMA_MODEL = 'boardinghouse.NotSchemaModel'
        with self.assertRaises(ImproperlyConfigured):
            get_schema_model()

    @modify_settings()
    def test_invalid_schema_model_string(self):
        settings.BOARDINGHOUSE_SCHEMA_MODEL = 'foo__bar'
        with self.assertRaises(ImproperlyConfigured):
            get_schema_model()

    @modify_settings()
    def test_swappable_model_changes_schema_template_verbose_names(self):
        settings.BOARDINGHOUSE_SCHEMA_MODEL = 'tests.NaiveModel'
        from boardinghouse.contrib.template.models import SchemaTemplate
        self.assertEqual('template naive model', six.text_type(SchemaTemplate._meta.verbose_name))
        self.assertEqual('template naive models', six.text_type(SchemaTemplate._meta.verbose_name_plural))
