from django.test import TestCase

from boardinghouse.models import Schema
from boardinghouse.schema import get_active_schema_name


class TestSchemaQuerysetMethods(TestCase):
    def test_active(self):
        Schema.objects.mass_create('a', 'b', 'c')
        self.assertEqual(
            set(['a', 'b', 'c']),
            set(Schema.objects.active().values_list('schema', flat=True))
        )

        Schema.objects.filter(schema='a').update(is_active=False)
        self.assertEqual(
            set(['b', 'c']),
            set(Schema.objects.active().values_list('schema', flat=True))
        )

    def test_inactive(self):
        Schema.objects.mass_create('a', 'b', 'c')
        self.assertEqual(
            set([]),
            set(Schema.objects.inactive().values_list('schema', flat=True))
        )

        Schema.objects.filter(schema='a').delete()
        self.assertEqual(
            set(['a']),
            set(Schema.objects.inactive().values_list('schema', flat=True))
        )

        Schema.objects.get(schema='b').delete()
        self.assertEqual(
            set(['a', 'b']),
            set(Schema.objects.inactive().values_list('schema', flat=True))
        )

    def test_queryset_activate_method(self):
        Schema.objects.mass_create('a', 'b', 'c')
        Schema().deactivate()

        self.assertEqual(None, get_active_schema_name())

        Schema.objects.activate('a')

        self.assertEqual('a', get_active_schema_name())
