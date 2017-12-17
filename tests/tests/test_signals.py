try:
    from unittest.mock import Mock, call
except ImportError:
    from mock import Mock, call

from django.contrib.auth.models import User, Group, Permission
from django.http import HttpRequest
from django.test import TestCase

from boardinghouse.middleware import change_schema
from boardinghouse.models import Schema
from boardinghouse.schema import TemplateSchemaActivation
from boardinghouse.signals import (
    session_requesting_schema_change, schema_aware_operation, session_schema_changed,
    find_schema,
)


class TestSignalsDirectly(TestCase):
    def test_template_activation_still_raises(self):
        with self.assertRaises(TemplateSchemaActivation):
            session_requesting_schema_change.send(sender=None, user=None, schema='__template__', session={})

    def test_schema_aware_operation(self):
        Schema.objects.mass_create('a', 'b', 'c')
        function = Mock()
        calls = [
            call('arg', kwarg=1),   # a
            call('arg', kwarg=1),   # b
            call('arg', kwarg=1),   # c
            call('arg', kwarg=1),   # __template__
        ]
        schema_aware_operation.send(sender=self,
                                    db_table='tests_awaremodel',
                                    function=function,
                                    args=['arg'],
                                    kwargs={'kwarg': 1})
        function.assert_has_calls(calls)
        self.assertEqual(4, function.call_count)

    def test_session_requesting_schema_change_may_return_dict(self):
        DATA = {
            'schema': '_spam',
            'name': 'eggs'
        }

        def pre_handler(**kwargs):
            return DATA

        post_handler = Mock()
        request = Mock(spec=HttpRequest,
                       user=Mock(wraps=User(), schemata=Mock()),
                       session={})

        session_requesting_schema_change.connect(pre_handler, sender=None)
        session_schema_changed.connect(post_handler, sender=None)

        change_schema(request, schema=Schema(**DATA))

        session_requesting_schema_change.disconnect(pre_handler, sender=None)
        session_schema_changed.disconnect(post_handler, sender=None)

        self.assertEqual(request.session, {
            'schema': '_spam',
            'schema_name': 'eggs'
        })
        self.assertEqual(1, post_handler.call_count)

    def test_session_schema_change_clears_permissions_caches(self):
        schema = Schema.objects.mass_create('a')[0]
        user = User.objects.create_user(username='username', password='password')
        schema.activate()
        user.groups.add(Group.objects.create(name='Group'))
        user.user_permissions.add(Permission.objects.all()[0])
        user.get_all_permissions()

        session_schema_changed.send(user=user, session=None, sender=None)

        with self.assertRaises(AttributeError):
            user._perm_cache
        with self.assertRaises(AttributeError):
            user._user_perm_cache
        with self.assertRaises(AttributeError):
            user._group_perm_cache

    def test_find_schema_finds_template(self):
        self.assertTrue([
            response for handler, response in find_schema.send(sender=None, schema='__template__')
            if response
        ][0])
