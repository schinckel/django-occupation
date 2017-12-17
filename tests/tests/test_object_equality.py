from django.test import TestCase

from boardinghouse.schema import get_schema_model
from ..models import AwareModel, NaiveModel

Schema = get_schema_model()


class TestObjectEquality(TestCase):
    def test_objects_from_different_schema_differ(self):
        first, second = Schema.objects.mass_create('first', 'second')

        first.activate()
        object_1 = AwareModel.objects.create(name="foo")

        second.activate()
        object_2 = AwareModel.objects.create(name="foo")

        self.assertEqual(object_1.pk, object_2.pk)
        self.assertNotEqual(object_1,
                            object_2,
                            "Objects with the same id from different schemata should not be equal.")

    def test_objects_from_same_schema_equal(self):
        first, second = Schema.objects.mass_create('first', 'second')

        first.activate()
        AwareModel.objects.create(name="foo")

        second.activate()
        object_2 = AwareModel.objects.create(name="foo")
        object_3 = AwareModel.objects.get(name="foo")

        self.assertEqual(object_2, object_3)

    def test_compare_aware_and_naive_objects(self):
        Schema.objects.create(name='schema', schema='schema').activate()
        aware = AwareModel.objects.create(name='foo', id=1)
        naive = NaiveModel.objects.create(name='foo', id=1)

        self.assertEqual(aware.pk, naive.pk)
        self.assertNotEqual(aware, naive)
