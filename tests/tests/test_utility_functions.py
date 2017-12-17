try:
    from unittest.mock import patch
except ImportError:
    from mock import patch

from django.test import TestCase, override_settings
from django.db import connection

from boardinghouse.schema import (
    is_shared_model, is_shared_table,
    activate_template_schema, deactivate_schema,
)

from ..models import (
    AwareModel,
    CoReferentialModelA,
    CoReferentialModelB,
    ModelA,
    ModelB,
    ModelBPrefix,
    NaiveModel,
    SelfReferentialModel,
)


class TestIsSharedModel(TestCase):
    def test_aware_model(self):
        self.assertFalse(is_shared_model(AwareModel()))

    def test_naive_model(self):
        self.assertTrue(is_shared_model(NaiveModel()))

    def test_self_referential_model(self):
        self.assertFalse(is_shared_model(SelfReferentialModel()))

    def test_co_referential_models(self):
        self.assertFalse(is_shared_model(CoReferentialModelA()))
        self.assertFalse(is_shared_model(CoReferentialModelB()))

    def test_contrib_models(self):
        from django.contrib.admin.models import LogEntry
        from django.contrib.auth.models import User, Group, Permission

        self.assertTrue(is_shared_model(User()))
        self.assertTrue(is_shared_model(Permission()))
        self.assertTrue(is_shared_model(Group()))
        self.assertTrue(is_shared_model(LogEntry()))

    def test_prefix(self):
        self.assertFalse(is_shared_model(ModelA))
        self.assertFalse(is_shared_model(ModelB))
        self.assertFalse(is_shared_model(ModelBPrefix))


class TestIsSharedTable(TestCase):
    def test_schema_table(self):
        self.assertTrue(is_shared_table('boardinghouse_schema'))
        self.assertTrue(is_shared_table('boardinghouse_schema_users'))

    def test_aware_model_table(self):
        self.assertFalse(is_shared_table(AwareModel._meta.db_table))

    def test_naive_model_table(self):
        self.assertTrue(is_shared_table(NaiveModel._meta.db_table))

    def test_join_tables(self):
        self.assertTrue(is_shared_table('auth_group_permissions'))
        self.assertFalse(is_shared_table('auth_user_groups'))

    def test_prefix_clash(self):
        self.assertFalse(is_shared_table('tests_modelb'))


class TestTemplateSchemaActivation(TestCase):
    @override_settings(TEMPLATE_SCHEMA='__template_schema__')
    def test_exception_when_no_template_schema_found(self):
        with self.assertRaises(Exception):
            activate_template_schema()

    def test_deserialize_from_string_activates_template_schema(self):
        with patch('boardinghouse.schema.activate_template_schema') as activate_template_schema:
            deactivate_schema()
            connection.creation.deserialize_db_from_string('[]')
            activate_template_schema.assert_called_once_with()
