from __future__ import unicode_literals
from importlib import import_module
import unittest

from django.db import ProgrammingError
from django.conf import settings
from django.contrib.auth.models import User, Group, Permission

from hypothesis import given, settings as hsettings
from hypothesis.strategies import text
from hypothesis.extra.django import TestCase

from boardinghouse.exceptions import Forbidden, SchemaNotFound
from boardinghouse.schema import get_schema_model, activate_schema
from boardinghouse.middleware import change_schema

from ..models import AwareModel

Schema = get_schema_model()
SessionStore = import_module(settings.SESSION_ENGINE).SessionStore

CREDENTIALS = {
    'username': 'test',
    'password': 'test'
}
SU_CREDENTIALS = {
    'username': 'su',
    'password': 'su',
    'email': 'su@example.com',
}


class TestMiddleware(TestCase):
    def test_view_without_schema_aware_models_works_without_activation(self):
        resp = self.client.get('/')
        self.assertEqual(200, resp.status_code)
        self.assertEqual(b'None', resp.content)

    def test_unauth_cannot_change_schema(self):
        first, second = Schema.objects.mass_create('first', 'second')

        resp = self.client.get('/', HTTP_X_CHANGE_SCHEMA='first')
        self.assertEqual(403, resp.status_code)

    @hsettings(max_examples=25)
    @given(text(min_size=1, alphabet='abcdefghijklmnopqrstuvwxyz_0123456789'))
    def test_invalid_schema(self, invalid):
        first, second = Schema.objects.mass_create('first', 'second')

        User.objects.create_superuser(
            username="su",
            password="su",
            email="su@example.com"
        )
        self.client.login(username='su', password='su')

        resp = self.client.get('/', HTTP_X_CHANGE_SCHEMA=invalid)
        self.assertEqual(403, resp.status_code)

        resp = self.client.get('/', HTTP_X_CHANGE_SCHEMA='second')
        self.assertEqual(b'second', resp.content)

        resp = self.client.get('/__change_schema__/{0}/'.format(invalid))
        self.assertEqual(403, resp.status_code)

        resp = self.client.get('/?__schema={0}'.format(invalid))
        self.assertEqual(403, resp.status_code)

    def test_only_one_available_schema(self):
        first, second = Schema.objects.mass_create('first', 'second')
        self.assertEqual(2, Schema.objects.count())

        user = User.objects.create_user(**CREDENTIALS)
        user.schemata.add(first)
        self.client.login(**CREDENTIALS)
        resp = self.client.get('/')
        self.assertEqual(b'first', resp.content)

    def test_middleware_activation(self):
        first, second = Schema.objects.mass_create('first', 'second')

        User.objects.create_superuser(**SU_CREDENTIALS)
        self.client.login(username='su', password='su')

        self.client.get('/__change_schema__/second/')
        resp = self.client.get('/')
        self.assertEqual(b'second', resp.content)

        resp = self.client.get('/', {'__schema': 'first'}, follow=True)
        self.assertEqual(b'first', resp.content)

        resp = self.client.get('/', {'__schema': 'second', 'foo': 'bar'}, follow=True)
        self.assertEqual(b'second\nfoo=bar', resp.content)

        resp = self.client.get('/', HTTP_X_CHANGE_SCHEMA='first')
        self.assertEqual(b'first', resp.content)

    def test_middleware_activation_on_post(self):
        Schema.objects.mass_create('first', 'second')

        User.objects.create_superuser(**SU_CREDENTIALS)
        self.client.login(username='su', password='su')

        self.client.post('/__change_schema__/second/')
        resp = self.client.post('/')
        self.assertEqual(b'second', resp.content)

        resp = self.client.post('/?__schema=first', follow=True)
        self.assertEqual(b'first', resp.content)

        resp = self.client.post('/?__schema=second&foo=bar', follow=True)
        self.assertEqual(b'second\nfoo=bar', resp.content)

        resp = self.client.post('/', HTTP_X_CHANGE_SCHEMA='first')
        self.assertEqual(b'first', resp.content)

    def test_non_superuser_schemata(self):
        Schema.objects.mass_create('a', 'b', 'c')
        user = User.objects.create_user(**CREDENTIALS)
        self.client.login(**CREDENTIALS)
        resp = self.client.get('/', {'__schema': 'a'}, follow=True)
        self.assertEqual(403, resp.status_code)

        user.schemata.add(Schema.objects.get(schema='a'))
        resp = self.client.get('/')
        self.assertEqual(b'a', resp.content)

        user.schemata.add(Schema.objects.get(schema='c'))
        resp = self.client.get('/')
        self.assertEqual(b'a', resp.content)

    def test_exception_caused_by_no_active_schema(self):
        Schema.objects.create(schema='a', name='a').activate()
        AwareModel.objects.create(name='foo')
        AwareModel.objects.create(name='bar')

        User.objects.create_user(**CREDENTIALS)
        self.client.login(**CREDENTIALS)
        resp = self.client.get('/')
        self.assertEqual(200, resp.status_code)
        self.assertEqual(b'None', resp.content)

        resp = self.client.get('/aware/')
        self.assertEqual(302, resp.status_code)

    def test_exception_caused_by_no_active_schema_ajax(self):
        Schema.objects.create(schema='a', name='a').activate()
        AwareModel.objects.create(name='foo')
        AwareModel.objects.create(name='bar')

        User.objects.create_user(**CREDENTIALS)
        self.client.login(**CREDENTIALS)
        resp = self.client.get('/aware/', HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(400, resp.status_code)

    def test_attempt_to_activate_template_schema(self):
        User.objects.create_user(**CREDENTIALS)
        self.client.login(**CREDENTIALS)

        resp = self.client.get('/', {'__schema': '__template__'}, follow=True)
        self.assertEqual(403, resp.status_code)

        resp = self.client.get('/__change_schema__/__template__/')
        self.assertEqual(403, resp.status_code)

        resp = self.client.get('/', HTTP_X_CHANGE_SCHEMA='__template__')
        self.assertEqual(403, resp.status_code)

    def test_attempt_to_activate_inactive_schema(self):
        schema = Schema.objects.create(schema='a', name='a', is_active=False)
        user = User.objects.create_user(**CREDENTIALS)
        user.schemata.add(schema)

        self.client.login(**CREDENTIALS)
        resp = self.client.get('/', {'__schema': 'a'}, follow=True)
        self.assertEqual(403, resp.status_code, 'Attempt to activate inactive schema succeeded!')

    def test_superuser_allowed_to_activate_inactive_schema(self):
        schema = Schema.objects.create(schema='a', name='a', is_active=False)
        Schema.objects.mass_create('b', 'c')
        superuser = User.objects.create_superuser(email='su@example.com', **CREDENTIALS)
        superuser.schemata.add(schema)

        self.client.login(**CREDENTIALS)
        resp = self.client.get('/', {'__schema': 'a'}, follow=True)
        self.assertEqual(200, resp.status_code, 'Superuser attempt to activate inactive schema failed!')

    def test_superuser_allowed_to_implicitly_activate_only_schema(self):
        schema = Schema.objects.create(schema='a', name='a')
        Schema.objects.mass_create('b', 'c')
        superuser = User.objects.create_superuser(email='su@example.com', **CREDENTIALS)
        superuser.schemata.add(schema)

        self.client.login(**CREDENTIALS)
        resp = self.client.get('/')
        self.assertEqual(200, resp.status_code, 'Superuser attempt to implicitly activate only schema failed!')

    def test_deactivate_schema(self):
        schema = Schema.objects.create(schema='a', name='a', is_active=False)
        superuser = User.objects.create_superuser(email='su@example.com', **CREDENTIALS)
        superuser.schemata.add(schema)

        self.client.login(**CREDENTIALS)
        resp = self.client.get('/__change_schema__/a/')
        resp = self.client.get('/__change_schema__//')
        self.assertEqual(b'Schema deselected', resp.content)

    def test_schema_set_to_same_value(self):
        Schema.objects.mass_create('a', 'b', 'c')
        user = User.objects.create_user(**CREDENTIALS)
        user.schemata.add(Schema.objects.get(schema='a'))
        self.client.login(**CREDENTIALS)
        resp = self.client.get('/', {'__schema': 'a'}, follow=True)
        self.assertEqual(b'a', resp.content)
        resp = self.client.get('/', {'__schema': 'a'}, follow=True)
        self.assertEqual(b'a', resp.content)

    def test_other_db_error_not_handled_by_us(self):
        with self.assertRaises(ProgrammingError):
            self.client.get('/sql/?sql=foo')

    def test_missing_table_when_schema_set(self):
        a = Schema.objects.create(name='a', schema='a')
        user = User.objects.create_user(**CREDENTIALS)
        user.schemata.add(a)

        self.client.login(**CREDENTIALS)
        self.client.get('/', {'__schema': 'a'})

        with self.assertRaises(ProgrammingError):
            response = self.client.get('/sql/?sql=SELECT+1+FROM+foo.bar')

    def test_explicit_change_to_inactive_schema(self):
        Schema.objects.mass_create('a', 'b', 'c')
        user = User.objects.create_user(**CREDENTIALS)
        user.schemata.add(*Schema.objects.all())
        Schema.objects.get(schema='b').delete()

        class Request(object):
            pass

        request = Request()
        request.user = user
        request.session = SessionStore()

        with self.assertRaises(Forbidden):
            change_schema(request, 'b')

    def test_view_changes_to_template_schema(self):
        response = self.client.get('/bad/activate/schema/__template__/')
        self.assertEqual(403, response.status_code)

    def test_session_schema_change_clears_permissions_caches(self):
        schema = Schema.objects.mass_create('a')[0]
        user = User.objects.create_user(username='username', password='password')
        user.schemata.add(schema)
        schema.activate()
        user.groups.add(Group.objects.create(name='Group'))
        user.user_permissions.add(Permission.objects.all()[0])
        user.get_all_permissions()

        class Request(object):
            pass

        request = Request()
        request.user = user
        request.session = SessionStore()

        change_schema(request=request, schema='a')

        with self.assertRaises(AttributeError):
            user._perm_cache
        with self.assertRaises(AttributeError):
            user._user_perm_cache
        with self.assertRaises(AttributeError):
            user._group_perm_cache

    def test_deleting_schema_removes_it_from_session(self):
        schema = Schema.objects.mass_create('a')[0]
        user = User.objects.create_user(**CREDENTIALS)
        user.schemata.add(schema)

        self.client.login(**CREDENTIALS)
        self.client.post('/__change_schema__/a/')
        self.assertTrue('a', self.client.session['schema'])

        schema.delete(drop=True)
        self.assertEqual(0, Schema.objects.count())

        with self.assertRaises(SchemaNotFound):
            activate_schema('a')

        self.client.get('/')
        self.assertFalse('schema' in self.client.session)


class TestContextProcessor(TestCase):
    def setUp(self):
        Schema.objects.mass_create('a', 'b', 'c')

    def test_no_schemata_if_anonymous(self):
        response = self.client.get('/change/')
        self.assertNotIn('schemata', response.context)
        self.assertNotIn('selected_schema', response.context)
        self.assertNotIn('schema_choices', response.context)

    def test_schemata_in_context(self):
        user = User.objects.create_user(**CREDENTIALS)
        schemata = Schema.objects.exclude(schema='b')
        user.schemata.add(*schemata)
        self.client.login(**CREDENTIALS)
        resp = self.client.get('/change/')
        self.assertEqual(2, len(resp.context['schemata']))
        self.assertIn(schemata[0], resp.context['schemata'])
        self.assertIn(schemata[1], resp.context['schemata'])
        self.assertEqual(None, resp.context['selected_schema'])

        resp = self.client.get('/change/', HTTP_X_CHANGE_SCHEMA='a')
        self.assertEqual(2, len(resp.context['schemata']))
        self.assertIn(schemata[0], resp.context['schemata'])
        self.assertIn(schemata[1], resp.context['schemata'])
        self.assertEqual('a', resp.context['selected_schema'])

    def test_user_has_no_schemata(self):
        User.objects.create_user(**CREDENTIALS)
        self.client.login(**CREDENTIALS)
        resp = self.client.get('/change/')
        self.assertEqual([], list(resp.context['schemata']))
        self.assertEqual([], list(resp.context['schema_choices']))
