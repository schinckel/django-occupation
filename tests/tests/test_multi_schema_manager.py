from django.test import TestCase

from boardinghouse.schema import get_schema_model
from ..models import AwareModel

Schema = get_schema_model()


class TestMultiSchemaManager(TestCase):
    def test_multi_schema_fetches_objects_correctly(self):
        Schema.objects.mass_create('a', 'b')

        a = Schema.objects.get(name='a')
        a.activate()
        AwareModel.objects.create(name='foo')
        AwareModel.objects.create(name='bar')
        AwareModel.objects.create(name='baz')

        b = Schema.objects.get(name='b')
        b.activate()
        AwareModel.objects.create(name='foo')
        AwareModel.objects.create(name='bar')
        AwareModel.objects.create(name='baz')

        b.deactivate()

        objects = list(AwareModel.objects.from_schemata(a))
        self.assertEqual(3, len(objects))

        objects = list(AwareModel.objects.from_schemata(a, b))
        self.assertEqual(6, len(objects))

    def test_ensure_multi_schema_fetched_objects_with_same_pk_differ(self):
        a = Schema.objects.create(name='a', schema='a')
        a.activate()
        AwareModel.objects.create(name='foo', pk=1)

        b = Schema.objects.create(name='b', schema='b')
        b.activate()
        AwareModel.objects.create(name='foo', pk=1)

        b.deactivate()

        objects = list(AwareModel.objects.from_schemata(a, b))
        self.assertEqual(2, len(objects))
        self.assertEqual(objects[0], objects[0])
        self.assertNotEqual(objects[0]._schema, None)
        self.assertNotEqual(objects[0]._schema, objects[1]._schema, 'MultiSchemaManager should tag _schema attribute on models.')
