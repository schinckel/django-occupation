import functools

from django.apps import apps
from django.conf import settings
from django.db import connection, transaction


@functools.lru_cache(maxsize=2)
def get_tenant_model():
    return apps.get_model(*settings.OCCUPATION_TENANT_MODEL.split('.'))


def get_tenant_fk(model):
    Tenant = get_tenant_model()

    for field in model._meta.fields:
        if field.related_model is Tenant:
            return field


ENABLE_RLS = 'ALTER TABLE {table_name} ENABLE ROW LEVEL SECURITY'
FORCE_RLS = 'ALTER TABLE {table_name} FORCE ROW LEVEL SECURITY'
CREATE_POLICY = 'CREATE POLICY access_tenant_data ON {table_name} USING ({policy}) WITH CHECK ({policy})'

CREATE_SUPERUSER_POLICY = '''
CREATE POLICY superuser_access_tenant_data ON {table_name} USING (is_superuser(current_setting('occupation.user_id')))
'''


def enable_row_level_security(model, superuser=False):
    policy_clauses = get_policy_clauses(model)

    if not policy_clauses:
        raise Exception('Unable to find any FK chains back to tenant model.')

    data = {
        'table_name': model._meta.db_table,
        'policy': ' AND '.join(policy_clauses)
    }

    with transaction.atomic():
        with connection.cursor() as cursor:
            cursor.execute(ENABLE_RLS.format(**data))
            cursor.execute(FORCE_RLS.format(**data))
            cursor.execute(CREATE_POLICY.format(**data))
            if superuser:
                cursor.execute(CREATE_SUPERUSER_POLICY.format(**data))


def get_fk_chains(model, root, parents=()):
    for field in model._meta.fields:
        if field.related_model is root:
            yield parents + (field,)
        elif field.related_model:
            for chain in get_fk_chains(field.related_model, root, parents + (field,)):
                yield parents + chain


def get_policy_clauses(model):
    Tenant = get_tenant_model()

    fields = set(field[0] for field in get_fk_chains(model, Tenant))
    DIRECT_LINK = "{fk}::TEXT = current_setting('occupation.active_tenant')"
    INDIRECT_LINK = "{fk} IN (SELECT {pk} FROM {table_name})"

    return [
        (DIRECT_LINK if field.related_model is Tenant else INDIRECT_LINK).format(
            fk=db_column(field),
            pk=db_column(field.remote_field.target_field),
            table_name=field.related_model._meta.db_table
        ) for field in fields
    ]


def db_column(field):
    return field.db_column or field.attname
