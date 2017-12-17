import datetime

try:
    from unittest.mock import patch
except ImportError:
    from mock import patch

from django.contrib.auth.models import User
from django.core.management import call_command
try:
    from django.urls import reverse
except ImportError:
    from django.core.urlresolvers import reverse
from django.db import migrations, models, connection
from django.db.migrations.state import ProjectState
from django.test import TestCase, override_settings
from django.utils import timezone, six

import pytz

from .utils import get_table_list
from ..models import AwareModel

from boardinghouse.contrib.demo import apps
from boardinghouse.contrib.demo.models import DemoSchema, DemoSchemaExpired, ValidDemoTemplate
from boardinghouse.contrib.template.models import SchemaTemplate
from boardinghouse.schema import _schema_exists, _get_schema

CREDENTIALS = {
    'username': 'username',
    'password': 'password'
}


class TestContribDemo(TestCase):
    def setUp(self):
        self.template = SchemaTemplate.objects.create(name='demo_template')
        ValidDemoTemplate.objects.create(template_schema=self.template)

    def test_demo_schema_name(self):
        user = User.objects.create_user(**CREDENTIALS)
        schema = DemoSchema.objects.create(user=user, from_template=self.template)
        self.assertEqual('Demo schema (demo_template)', six.text_type(schema.name))

    def test_demo_schema_str(self):
        demo = DemoSchema(user=User(username='user'),
                          expires_at=datetime.datetime.now().replace(tzinfo=pytz.utc) + datetime.timedelta(1),
                          from_template=self.template)
        self.assertTrue(six.text_type(demo).startswith('Demo for user: expires at'))
        demo.expires_at = datetime.datetime(1970, 1, 1, tzinfo=pytz.utc)
        self.assertTrue(six.text_type(demo).startswith('Expired demo for user (expired'))

    def test_valid_demo_template_str(self):
        template = SchemaTemplate.objects.create(name='xxx')
        demo_template = ValidDemoTemplate.objects.create(template_schema=template)
        self.assertEqual('xxx is valid as a demo source', str(demo_template))

    def test_demo_can_be_created_and_activated(self):
        user = User.objects.create_user(**CREDENTIALS)
        schema = DemoSchema.objects.create(user=user, from_template=self.template)
        schema.activate()
        schema.deactivate()

    def test_demo_can_only_be_activated_by_user(self):
        User.objects.create_user(**CREDENTIALS)
        other = User.objects.create_user(username='other', password='password')
        DemoSchema.objects.create(user=other, from_template=self.template)

        self.client.login(**CREDENTIALS)
        response = self.client.get('/aware/?__schema=__demo_{0}'.format(other.pk))
        self.assertEqual(403, response.status_code)

    def test_demo_can_be_activated_by_user(self):
        user = User.objects.create_user(**CREDENTIALS)
        DemoSchema.objects.create(user=user, from_template=self.template)
        self.client.login(**CREDENTIALS)
        response = self.client.get('/__change_schema__/__demo_{0}/'.format(user.pk))
        self.assertEqual(200, response.status_code)

    def test_activation_of_expired_demo_raises(self):
        user = User.objects.create_user(**CREDENTIALS)
        schema = DemoSchema.objects.create(user=user,
                                           expires_at=timezone.now().replace(tzinfo=pytz.utc),
                                           from_template=self.template)
        with self.assertRaises(DemoSchemaExpired):
            schema.activate()

    def test_cleanup_expired_removes_expired(self):
        user = User.objects.create_user(**CREDENTIALS)
        demo = DemoSchema.objects.create(user=user, expires_at='1970-01-01T00:00:00Z', from_template=self.template)
        self.assertTrue(_schema_exists(demo.schema))

        call_command('cleanup_expired_demos')

        self.assertEqual(0, DemoSchema.objects.count())
        self.assertFalse(_schema_exists(demo.schema))

    def test_deletion_of_demo_drops_schema(self):
        user = User.objects.create_user(**CREDENTIALS)
        demo = DemoSchema.objects.create(user=user, from_template=self.template)
        self.assertTrue(_schema_exists(demo.schema))
        demo.delete()
        self.assertFalse(_schema_exists(demo.schema))

    def test_find_schema_finds_demo(self):
        user = User.objects.create_user(**CREDENTIALS)
        demo = DemoSchema.objects.create(user=user, from_template=self.template)
        self.assertEqual(demo, _get_schema(demo.schema))

    def test_demo_admin(self):
        user = User.objects.create_superuser(email='email@example.com', **CREDENTIALS)
        DemoSchema.objects.create(user=User.objects.create_user(username='a', password='a'),
                                  expires_at='1970-01-01T00:00:00Z',
                                  from_template=self.template)
        DemoSchema.objects.create(user=User.objects.create_user(username='b', password='b'),
                                  expires_at='9999-01-01T00:00:00Z',
                                  from_template=self.template)

        self.client.login(**CREDENTIALS)

        response = self.client.get(reverse('admin:demo_demoschema_changelist'))
        self.assertContains(response, '/static/admin/img/icon-no', count=1, status_code=200)
        self.assertContains(response, '/static/admin/img/icon-yes', count=1, status_code=200)

        # Create a template, because we need to.
        response = self.client.get(reverse('admin:template_schematemplate_add'))
        self.assertEqual(200, response.status_code)
        response = self.client.post(reverse('admin:template_schematemplate_add'), data={
            'name': 'template',
            'is_active': 'on',
            'use_for_demo-TOTAL_FORMS': '0',
            'use_for_demo-INITIAL_FORMS': '0',
        })
        self.assertEqual(302, response.status_code)
        template = SchemaTemplate.objects.get(name='template')
        # Ensure cannot select as template for demo when not set.
        response = self.client.post(reverse('admin:demo_demoschema_add'), data={
            'user': user.pk,
            'from_template': template.pk,
        })
        self.assertEqual(200, response.status_code)
        self.assertTrue('from_template' in response.context['adminform'].form.errors)
        # Exercise some of the admin pages
        response = self.client.get(reverse('admin:template_schematemplate_change', args=(template.pk,)))
        self.assertEqual(200, response.status_code)
        # Make this template a valid demo source.
        response = self.client.post(reverse('admin:template_schematemplate_change', args=(template.pk,)), data={
            'name': 'template',
            'is_active': 'on',
            'use_for_demo-TOTAL_FORMS': '1',
            'use_for_demo-INITIAL_FORMS': '0',
            'use_for_demo-0-use_for_demo': 'on',
            'use_for_demo-0-template_schema': template.pk,
        })
        self.assertEqual(302, response.status_code)
        response = self.client.get(reverse('admin:template_schematemplate_change', args=(template.pk,)))
        self.assertEqual(200, response.status_code)

        response = self.client.get(reverse('admin:demo_demoschema_change', args=(DemoSchema.objects.all()[0].pk,)))
        self.assertEqual(200, response.status_code)
        response = self.client.get(reverse('admin:demo_demoschema_add'))
        self.assertEqual(200, response.status_code)
        response = self.client.post(reverse('admin:demo_demoschema_add'), data={
            'user': user.pk,
            'from_template': template.pk,
        })
        self.assertEqual(302, response.status_code)
        response = self.client.post(reverse('admin:demo_demoschema_change', args=(user.pk,)), data={
            'expires_at_0': '2016-01-01',
            'expires_at_1': '00:00:00',
        })
        self.assertEqual(302, response.status_code)
        self.assertEqual(datetime.date(2016, 1, 1),
                         DemoSchema.objects.get(user=user).expires_at.date())

        self.assertEqual(2, ValidDemoTemplate.objects.count())
        response = self.client.post(reverse('admin:template_schematemplate_change', args=(template.pk,)), data={
            'name': 'template',
            'is_active': 'on',
            'use_for_demo-TOTAL_FORMS': '1',
            'use_for_demo-INITIAL_FORMS': '1',
            'use_for_demo-0-template_schema': template.pk,
        })
        self.assertEqual(302, response.status_code)
        self.assertEqual(1, ValidDemoTemplate.objects.count())
        response = self.client.get(reverse('admin:template_schematemplate_changelist'))
        self.assertEqual(200, response.status_code)

    def test_demo_schemata_get_migrated(self):
        user = User.objects.create_user(**CREDENTIALS)
        schema = DemoSchema.objects.create(user=user, from_template=self.template)

        operation = migrations.CreateModel("Pony", [
            ('pony_id', models.AutoField(primary_key=True)),
            ('pink', models.IntegerField(default=1)),
        ])
        project_state = ProjectState()
        new_state = project_state.clone()
        operation.state_forwards('tests', new_state)

        schema.activate()
        self.assertFalse('tests_pony' in get_table_list())

        with connection.schema_editor() as editor:
            operation.database_forwards('tests', editor, project_state, new_state)
        schema.activate()
        self.assertTrue('tests_pony' in get_table_list())

        with connection.schema_editor() as editor:
            operation.database_backwards('tests', editor, new_state, project_state)
        schema.activate()
        self.assertFalse('tests_pony' in get_table_list())

    @override_settings(BOARDINGHOUSE_DEMO_PERIOD=datetime.timedelta(7))
    def test_default_expiry_period_from_settings(self):
        user = User.objects.create_user(**CREDENTIALS)
        schema = DemoSchema.objects.create(user=user, from_template=self.template)

        self.assertEqual(timezone.now().date() + datetime.timedelta(7), schema.expires_at.date())

    @override_settings(BOARDINGHOUSE_DEMO_PERIOD='not-a-valid-timedelta')
    def test_invalid_expiry(self):
        errors = apps.check_demo_expiry_is_timedelta()
        self.assertEqual(1, len(errors))
        self.assertEqual('boardinghouse.contrib.demo.E002', errors[0].id)

    @override_settings(BOARDINGHOUSE_DEMO_PREFIX='demo_')
    def test_invalid_prefix(self):
        errors = apps.check_demo_prefix_stats_with_underscore()
        self.assertEqual(1, len(errors))
        self.assertEqual('boardinghouse.contrib.demo.E001', errors[0].id)

    def test_contrib_template_installed(self):
        with patch('django.apps.apps', **{'is_installed.return_value': False}):
            errors = apps.ensure_contrib_template_installed()
            self.assertEqual(1, len(errors))
            self.assertEqual('boardinghouse.contrib.demo.E003', errors[0].id)

    def test_demo_lifecycle_views(self):
        CREATE_DEMO = reverse('demo:create')
        RESET_DEMO = reverse('demo:reset')
        DELETE_DEMO = reverse('demo:delete')

        response = self.client.post(CREATE_DEMO)
        self.assertEqual(302, response.status_code, 'Unauthenticated user should be redirected to login')

        user = User.objects.create_user(**CREDENTIALS)
        self.client.login(**CREDENTIALS)

        # reset and delete should fail with 404 when no DemoSchema for current user.
        response = self.client.post(DELETE_DEMO)
        self.assertEqual(404, response.status_code, 'DELETE when no DemoSchema should return 404')
        response = self.client.post(RESET_DEMO)
        self.assertEqual(404, response.status_code, 'RESET when no DemoSchema should return 404')

        # Create without from_template should fail with 409.
        response = self.client.post(CREATE_DEMO)
        self.assertEqual(409, response.status_code, 'Missing from_template should result in 409')

        response = self.client.post(CREATE_DEMO, data={'from_template': self.template.pk})
        self.assertEqual(302, response.status_code, 'Successful creation of demo should redirect')
        demo_schema = DemoSchema.objects.get(user=user)
        self.assertTrue('/__change_schema__/{0}/'.format(demo_schema.schema))

        # Create should fail: as template already exists.
        response = self.client.post(CREATE_DEMO, data={'from_template': self.template.pk})
        self.assertEqual(409, response.status_code, 'Existing DemoSchema should result in 409')

        demo = DemoSchema.objects.get(user=user)
        demo.activate()

        AwareModel.objects.create(name='foo', status=True)

        self.assertEqual(1, AwareModel.objects.count(), 'One object created before reset')
        response = self.client.post(RESET_DEMO)
        demo = DemoSchema.objects.get(user=user)
        demo.activate()
        self.assertEqual(0, AwareModel.objects.count(), 'Reset should clear out any objects from schema')

        response = self.client.post(DELETE_DEMO)
        self.assertFalse(DemoSchema.objects.filter(user=user).exists(), 'Delete should remove schema')
        self.assertFalse(_schema_exists(demo.schema))
