from django.db import connection
from django.utils import six


def get_table_list():
    with connection.cursor() as cursor:
        table_list = connection.introspection.get_table_list(cursor)
    if table_list and not isinstance(table_list[0], six.string_types):
        table_list = [table.name for table in table_list]
    return table_list
