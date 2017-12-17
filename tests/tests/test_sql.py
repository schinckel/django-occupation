"""
Tests for the RAW sql functions.
"""

from django.test import TestCase
from django.db import connection

from boardinghouse.models import Schema


class TestRejectSchemaColumnChange(TestCase):
    def test_exception_is_raised(self):
        Schema.objects.mass_create('a')
        cursor = connection.cursor()
        UPDATE = "UPDATE boardinghouse_schema SET schema='foo' WHERE schema='a'"
        self.assertRaises(Exception, cursor.execute, UPDATE)
