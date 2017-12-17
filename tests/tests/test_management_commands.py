# -*- coding: utf-8 -*-

import json
import sys
import unittest

from contextlib import contextmanager

from django.core.management import call_command
from django.db import connection, DatabaseError
from django.test import TestCase
from django.utils import six

from boardinghouse.schema import get_active_schema, get_schema_model
from boardinghouse.exceptions import TemplateSchemaActivation, SchemaNotFound, SchemaRequiredException

from ..models import AwareModel, NaiveModel

Schema = get_schema_model()

SCHEMA_QUERY = "SELECT schema_name FROM information_schema.schemata WHERE schema_name = %s"


@contextmanager
def capture(command, *args, **kwargs):
    out, sys.stdout = sys.stdout, six.StringIO()
    command(*args, **kwargs)
    sys.stdout.seek(0)
    yield sys.stdout.read()
    sys.stdout = out


@contextmanager
def capture_err(command, *args, **kwargs):
    err, sys.stderr = sys.stderr, six.StringIO()
    command(*args, **kwargs)
    sys.stderr.seek(0)
    yield sys.stderr.read()
    sys.stderr = err


class TestLoadData(TestCase):
    def test_invalid_schema_causes_error(self):
        with self.assertRaises(SchemaNotFound):
            call_command('loaddata', 'foo', schema='foo')

    def test_loading_schemata_creates_pg_schemata(self):
        self.assertEqual(0, Schema.objects.count())
        # Need to use commit=False, else the data will be in a different transaction.
        with capture(call_command, 'loaddata', 'tests/fixtures/schemata.json', commit=False) as output:
            self.assertEqual('Installed 2 object(s) from 1 fixture(s)\n', output)
        self.assertEqual(2, Schema.objects.count())
        Schema.objects.all()[0].activate()
        self.assertTrue(get_active_schema())
        cursor = connection.cursor()
        for schema in Schema.objects.all():
            cursor.execute(SCHEMA_QUERY, [schema.schema])
            data = cursor.fetchone()
            self.assertEqual((schema.schema,), data)
        cursor.close()

    def test_loading_naive_data_does_not_require_schema_arg(self):
        with capture(call_command, 'loaddata', 'tests/fixtures/naive.json', commit=False) as output:
            self.assertEqual('Installed 2 object(s) from 1 fixture(s)\n', output)
        NaiveModel.objects.get(name="naive1")

    def test_loading_naive_data_works_with_schema_passed_in(self):
        Schema.objects.create(name='a', schema='a')
        with capture(call_command, 'loaddata', 'tests/fixtures/naive.json', schema='a', commit=False) as output:
            self.assertEqual('Installed 2 object(s) from 1 fixture(s)\n', output)
        NaiveModel.objects.get(name="naive1")

    def test_loading_aware_data_without_a_schema_fails(self):
        with self.assertRaises(DatabaseError):
            with capture_err(call_command, 'loaddata', 'tests/fixtures/aware.json', commit=False) as output:
                self.assertIn('DatabaseError: Could not load tests.AwareModel(pk=None): relation "tests_awaremodel" does not exist\n', output)

    def test_loading_aware_data_with_template_schema_fails(self):
        with self.assertRaises(TemplateSchemaActivation):
            with capture_err(call_command, 'loaddata', 'tests/fixtures/aware.json', schema="__template__", commit=False) as output:
                self.assertIn('DatabaseError: Could not load tests.AwareModel(pk=None): relation "tests_awaremodel" does not exist\n', output)

    def test_loading_aware_data_works(self):
        Schema.objects.mass_create('a', 'b')
        with capture(call_command, 'loaddata', 'tests/fixtures/aware.json', schema='a', commit=False) as output:
            self.assertEqual('Installed 2 object(s) from 1 fixture(s)\n', output)

        Schema.objects.get(schema='a').activate()
        AwareModel.objects.get(name='aware1')

        Schema.objects.get(pk='b').activate()
        self.assertRaises(AwareModel.DoesNotExist, AwareModel.objects.get, name='aware1')

    @unittest.expectedFailure
    def test_loaddata_containing_schema_data_works(self):
        """
        This one is a fair way off: it would be great to be able to dump
        and load data from multiple schemata at once. I'm thinking the
        loading may be easier:)

        One solution would be to extract the fixture data, and then put it into N+1 files,
        where the first file is any fixtures without a referred-to schema, and all other
        files are all fixtures grouped by schema.

        This might require us to parse the file first, if --schema is not supplied, and look for
        any private models that don't have a schema attribute.

        We can't seem to inject anything into the deserialisation process, as it's a function,
        and there isn't really anywhere to inject code.
        """
        Schema.objects.mass_create('a', 'b')
        call_command('loaddata', 'tests/fixtures/aware_plus_schemata.json')
        with capture(call_command, 'loaddata', 'tests/fixtures/aware_plus_schemata.json', commit=False) as output:
            self.assertEqual('Installed 2 object(s) from 1 fixture(s)\n', output)

        Schema.objects.get(schema='a').activate()
        self.assertEqual('aware1', AwareModel.objects.get().name)

        Schema.objects.get(schema='b').activate()
        self.assertEqual(u'🌊🌊🌊🌊🌊', AwareModel.objects.get().name)


class TestDumpData(TestCase):
    def test_invalid_schema_raises_exception(self):
        with self.assertRaises(SchemaNotFound):
            call_command('dumpdata', 'tests', schema='foo')

    def test_dumpdata_on_naive_models_does_not_require_schema(self):
        with capture(call_command, 'dumpdata', 'boardinghouse') as output:
            self.assertEqual('[]', output)

    def test_dumpdata_on_aware_model(self):
        Schema.objects.mass_create('a', 'b')
        Schema.objects.get(schema='a').activate()
        AwareModel.objects.create(name='foo')

        with capture(call_command, 'dumpdata', 'tests.AwareModel', schema='a') as output:
            data = sorted(json.loads(output))

        self.assertEqual(1, len(data))
        self.assertEqual({"factor": 7, "status": False, "name": "foo"}, data[0]['fields'])

        with capture(call_command, 'dumpdata', 'tests.AwareModel', schema='b') as output:
            data = sorted(json.loads(output))

        self.assertEqual(0, len(data))

    def test_dumpdata_on_aware_model_requires_schema(self):
        with self.assertRaises(SchemaRequiredException):
            call_command('dumpdata', 'tests.awaremodel')
