from django.test import TestCase
from django.db import connection
from django import forms
from django.utils import six

from boardinghouse.schema import (
    activate_schema, deactivate_schema,
    TemplateSchemaActivation,
    is_shared_model,
    get_active_schema_name,
    get_schema_model,
    activate_template_schema,
    _get_search_path,
)

Schema = get_schema_model()

SCHEMA_QUERY = "SELECT schema_name FROM information_schema.schemata WHERE schema_name = %s"
TABLE_QUERY = "SELECT table_name FROM information_schema.tables WHERE table_schema = %s AND table_name = %s"


class TestPostgresSchemaCreation(TestCase):
    def test_schema_table_is_in_public(self):
        deactivate_schema()
        cursor = connection.cursor()
        table_name = Schema._meta.db_table
        cursor.execute(TABLE_QUERY, ['public', table_name])
        data = cursor.fetchone()
        self.assertEqual((table_name,), data)
        cursor.close()

    def test_template_schema_is_created(self):
        cursor = connection.cursor()
        cursor.execute(SCHEMA_QUERY, ['__template__'])
        data = cursor.fetchone()
        self.assertEqual(('__template__',), data)
        cursor.close()

    def test_schema_object_creation_creates_schema(self):
        Schema.objects.create(name="Test Schema", schema="test_schema")
        cursor = connection.cursor()
        cursor.execute(SCHEMA_QUERY, ['test_schema'])
        data = cursor.fetchone()
        self.assertEqual(('test_schema',), data)
        cursor.close()

    def test_schema_object_creation_does_not_leak_between_tests(self):
        cursor = connection.cursor()
        cursor.execute(SCHEMA_QUERY, ['test_schema'])
        data = cursor.fetchone()
        self.assertEqual(None, data)
        cursor.close()

    def test_schema_creation_clones_template(self):
        activate_template_schema()
        cursor = connection.cursor()
        cursor.execute("CREATE TABLE foo (id SERIAL NOT NULL PRIMARY KEY)")
        Schema.objects.create(name="Duplicate", schema='duplicate')
        cursor.execute(TABLE_QUERY, ['duplicate', 'foo'])
        data = cursor.fetchone()
        self.assertEqual(('foo',), data)
        cursor.close()

    def test_bulk_create_creates_schemata(self):
        schemata = ['first', 'second', 'third']
        Schema.objects.mass_create(*schemata)
        cursor = connection.cursor()
        for schema in schemata:
            activate_schema(schema)
            cursor.execute(SCHEMA_QUERY, [schema])
            data = cursor.fetchone()
            self.assertEqual((schema,), data)
        cursor.close()

    def test_mass_create(self):
        Schema.objects.mass_create('a', 'b', 'c')
        self.assertEqual(['a', 'b', 'c'], sorted(Schema.objects.values_list('pk', flat=True)))

    def test_schema_already_exists(self):
        cursor = connection.cursor()
        cursor.execute('CREATE SCHEMA already_here')
        with self.assertRaises(ValueError):
            Schema.objects.mass_create('already_here')


class TestSchemaDrop(TestCase):
    def test_dropping_schema_model(self):
        Schema.objects.mass_create('a', 'b')
        Schema.objects.get(schema='a').delete(drop=True)
        self.assertEqual(['b'],
            list(Schema.objects.values_list('pk', flat=True)))
        cursor = connection.cursor()
        cursor.execute(SCHEMA_QUERY, ['a'])
        self.assertFalse(cursor.fetchone())

    def test_dropping_schema_queryset(self):
        Schema.objects.mass_create('a', 'b', 'c')
        Schema.objects.filter(schema__in=['b', 'c']).delete(drop=True)
        six.assertCountEqual(self, ['a'],
            Schema.objects.values_list('pk', flat=True))

    def test_delete_is_soft_by_default_model(self):
        Schema.objects.mass_create('a', 'b', 'c')
        Schema.objects.get(schema='b').delete()
        six.assertCountEqual(self, ['a', 'b', 'c'],
            Schema.objects.values_list('pk', flat=True))

        six.assertCountEqual(self, ['a', 'c'],
            Schema.objects.active().values_list('schema', flat=True))

    def test_delete_is_soft_by_default_queryset(self):
        Schema.objects.mass_create('a', 'b', 'c', 'd')
        Schema.objects.filter(schema__in=['b', 'd']).delete()
        self.assertSequenceEqual(['a', 'b', 'c', 'd'],
            list(Schema.objects.order_by('schema').values_list('pk', flat=True)))

        self.assertSequenceEqual(['a', 'c'],
            list(Schema.objects.active().values_list('schema', flat=True)))

    def test_delete_of_non_existent_schema_is_fine_thankyou(self):
        Schema.objects.mass_create('a', 'b', 'c')
        cursor = connection.cursor()
        cursor.execute('DROP SCHEMA a CASCADE')
        Schema.objects.get(schema='a').delete()


class TestSchemaClassValidationLogic(TestCase):
    def test_ensure_schema_model_is_not_schema_aware(self):
        self.assertTrue(is_shared_model(Schema))
        self.assertTrue(is_shared_model(Schema()))

    def test_schema_schema_validation_rejects_invalid_chars(self):
        self.assertRaises(forms.ValidationError, Schema.objects.create, schema='_foo', name="1")
        self.assertRaises(forms.ValidationError, Schema.objects.create, schema='-foo', name="2")
        self.assertRaises(forms.ValidationError, Schema.objects.create, schema='a' * 37, name="3")
        self.assertRaises(forms.ValidationError, Schema.objects.create, schema='foo-1', name="4")
        self.assertRaises(forms.ValidationError, Schema.objects.create, schema='Foo', name="5")

    def test_schema_validation_allows_valid_chars(self):
        Schema.objects.create(schema='foo', name="Foo 1")
        Schema.objects.create(schema='a' * 36, name="Foo 2")
        Schema.objects.create(schema='foo_bar', name="Foo 3")

    def test_schema_rejects_duplicate_schema(self):
        Schema.objects.create(schema='foo', name="Foo")
        self.assertRaises(forms.ValidationError, Schema.objects.create, schema='foo', name="Foo 2")

    def test_schema_rejects_schema_change(self):
        schema = Schema.objects.create(schema='foo', name="Foo")
        schema.name = "Bar"
        schema.save()
        schema.schema = 'bar'
        self.assertRaises(forms.ValidationError, schema.save)


class TestGetSetSearchPath(TestCase):
    def test_default_search_path(self):
        self.assertEqual(None, get_active_schema_name())

    def test_manual_set_search_path(self):
        Schema.objects.create(name='a', schema='a')
        connection.cursor().execute('SET search_path TO a,public')
        self.assertEqual('a', get_active_schema_name())

    def test_activate_schema_sets_search_path(self):
        schema = Schema.objects.create(name='a', schema='a')
        schema.activate()
        self.assertEqual(schema.schema, get_active_schema_name())

        activate_template_schema()
        self.assertEqual('__template__', _get_search_path())

    def test_deactivate_schema_resets_search_path(self):
        schema = Schema.objects.create(name='a', schema='a')
        schema.activate()
        schema.deactivate()
        self.assertEqual(None, get_active_schema_name())

    def test_get_schema_or_template_helper(self):
        schema = Schema.objects.create(name='a', schema='a')
        self.assertEqual(None, get_active_schema_name())

        schema.activate()
        self.assertEqual('a', get_active_schema_name())

        schema.deactivate()
        self.assertEqual(None, get_active_schema_name())

    def test_activate_schema_function(self):
        self.assertRaises(TemplateSchemaActivation, activate_schema, '__template__')

        Schema.objects.mass_create('a', 'b')

        activate_schema('a')
        self.assertEqual('a', get_active_schema_name())

        activate_schema('b')
        self.assertEqual('b', get_active_schema_name())

        deactivate_schema()
        self.assertEqual(None, get_active_schema_name())
