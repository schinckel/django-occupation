import sys
import uuid

from django.test import TestCase, override_settings
from django.contrib.auth.models import User
from django.db import connection, migrations, models
from django.db.migrations.state import ProjectState
from django.utils import six

from boardinghouse.contrib.template.apps import check_template_prefix_stats_with_underscore
from boardinghouse.contrib.template.models import SchemaTemplate
from boardinghouse.contrib.template.models import verbose_name, verbose_name_plural

from boardinghouse.models import Schema
from boardinghouse.schema import (
    _schema_exists, _get_schema,
    get_active_schema_name,
)

from ..models import AwareModel
from .utils import get_table_list

CREDENTIALS = {
    'username': 'username',
    'password': 'password'
}


class TestContribTemplate(TestCase):
    def test_find_schema_finds_templates(self):
        template = SchemaTemplate.objects.create(name='Foo')
        self.assertEqual(template, _get_schema(template.schema))

    def test_template_str(self):
        template = SchemaTemplate(name='Foo')
        self.assertEqual(u'Foo', six.text_type(template))

    def test_templates_can_be_created_and_destroyed(self):
        template = SchemaTemplate.objects.create(name='Foo')
        self.assertTrue(_schema_exists(template.schema))
        template.activate()
        self.assertEqual(get_active_schema_name(), template.schema)
        template.deactivate()
        template.delete()
        self.assertFalse(_schema_exists(template.schema))

    def test_templates_cannot_be_activated_normally(self):
        template = SchemaTemplate.objects.create(name='Foo')
        User.objects.create_user(**CREDENTIALS)
        self.client.login(**CREDENTIALS)
        response = self.client.get('/__change_schema__/{0}/'.format(template.schema))
        self.assertEqual(403, response.status_code)

    def test_templates_can_be_activated_by_superuser(self):
        template = SchemaTemplate.objects.create(name='Foo')
        User.objects.create_superuser(email='superuser@example.com', **CREDENTIALS)
        self.client.login(**CREDENTIALS)
        response = self.client.get('/__change_schema__/{0}/'.format(template.schema))
        self.assertEqual(200, response.status_code)

    def test_invalid_template_raises_forbidden(self):
        template = SchemaTemplate.objects.create(name='Foo')
        User.objects.create_superuser(email='superuser@example.com', **CREDENTIALS)
        self.client.login(**CREDENTIALS)
        response = self.client.get('/__change_schema__/{0}1/'.format(template.schema))
        self.assertEqual(403, response.status_code)

    def test_cloning_templates_clones_data(self):
        template = SchemaTemplate.objects.create(name='Foo')
        template.activate()

        aware = AwareModel.objects.create(name=uuid.uuid4().hex[:10])

        schema = Schema(name='cloned', schema='cloned')
        schema._clone = template.schema
        schema.save()

        schema.activate()
        AwareModel.objects.get(name=aware.name)

    def test_editing_template_does_not_change_template_data(self):
        template = SchemaTemplate.objects.create(name='Foo')
        template.activate()

        original = AwareModel.objects.create(name=uuid.uuid4().hex[:10])

        schema = Schema(name='cloned', schema='cloned')
        schema._clone = template.schema
        schema.save()

        schema.activate()
        cloned = AwareModel.objects.get(name=original.name)
        cloned.status = True
        cloned.save()

        template.activate()
        self.assertEqual(1, AwareModel.objects.filter(status=False).count())
        self.assertEqual(0, AwareModel.objects.filter(status=True).count())

        schema.activate()
        self.assertEqual(0, AwareModel.objects.filter(status=False).count())
        self.assertEqual(1, AwareModel.objects.filter(status=True).count())

    def test_migrations_apply_to_templates(self):
        template = SchemaTemplate.objects.create(name='a')
        operation = migrations.CreateModel("Pony", [
            ('pony_id', models.AutoField(primary_key=True)),
            ('pink', models.IntegerField(default=1)),
        ])
        project_state = ProjectState()
        new_state = project_state.clone()
        operation.state_forwards('tests', new_state)

        template.activate()
        self.assertFalse('tests_pony' in get_table_list())

        with connection.schema_editor() as editor:
            operation.database_forwards('tests', editor, project_state, new_state)
        template.activate()
        self.assertTrue('tests_pony' in get_table_list())

        with connection.schema_editor() as editor:
            operation.database_backwards('tests', editor, new_state, project_state)
        template.activate()
        self.assertFalse('tests_pony' in get_table_list())

    def test_verbose_name_in_makemigrations(self):
        sys.argv.append('makemigrations')
        self.assertEqual('template schema', verbose_name())
        self.assertEqual('template schemata', verbose_name_plural())
        sys.argv.remove('makemigrations')

    def test_schema_template_queryset_active(self):
        SchemaTemplate.objects.create(name='a')
        SchemaTemplate.objects.create(name='b', is_active=False)
        SchemaTemplate.objects.create(name='c')

        self.assertEqual({'a', 'c'},
                         set(SchemaTemplate.objects.active().values_list('name', flat=True)))

    @override_settings(BOARDINGHOUSE_TEMPLATE_PREFIX='template_')
    def test_invalid_prefix(self):
        errors = check_template_prefix_stats_with_underscore()
        self.assertEqual(1, len(errors))
        self.assertEqual('boardinghouse.contrib.template.E001', errors[0].id)
