from django.apps import apps
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.db import connection, transaction


def get_tenant_model(apps=apps):
    try:
        return apps.get_model(settings.OCCUPATION_TENANT_MODEL, require_ready=False)
    except AttributeError:
        raise ImproperlyConfigured(
            "OCCUPATION_TENANT_MODEL is not set: is 'occupation' in your INSTALLED_APPS?"
        )
    except ValueError:
        raise ImproperlyConfigured(
            "OCCUPATION_TENANT_MODEL must be of the form 'app_label.model_name'."
        )
    except LookupError:
        raise ImproperlyConfigured(
            "OCCUPATION_TENANT_MODEL refers to the model '{0!s}' that has not been installed.".format(
                settings.OCCUPATION_TENANT_MODEL
            )
        )


ENABLE_RLS = 'ALTER TABLE {table_name} ENABLE ROW LEVEL SECURITY'
FORCE_RLS = 'ALTER TABLE {table_name} FORCE ROW LEVEL SECURITY'
DISABLE_RLS = 'ALTER TABLE {table_name} DISABLE ROW LEVEL SECURITY'
CREATE_POLICY = 'CREATE POLICY access_tenant_data ON {table_name} USING ({policy}) WITH CHECK ({policy})'
DROP_POLICY = 'DROP POLICY access_tenant_data ON {table_name}'

CREATE_SUPERUSER_POLICY = '''
CREATE POLICY superuser_access_tenant_data ON {table_name} USING (is_superuser(current_setting('occupation.user_id')))
'''
DROP_SUPERUSER_POLICY = 'DROP POLICY superuser_access_tenant_data ON {table_name}'


def enable_row_level_security(app_label, model_name, apps=apps, superuser=False):
    model = apps.get_model(app_label, model_name)

    policy_clauses = get_policy_clauses(model, get_tenant_model(apps))

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


def disable_row_level_security(app_label, model_name, apps=apps, superuser=False):
    model = apps.get_model(app_label, model_name)

    data = {
        'table_name': model._meta.db_table,
    }

    with transaction.atomic():
        with connection.cursor() as cursor:
            cursor.execute(DISABLE_RLS.format(**data))
            cursor.execute(DROP_POLICY.format(**data))
            if superuser:
                cursor.execute(DROP_SUPERUSER_POLICY.format(**data))


def get_fk_chains(model, root, parents=()):
    for field in model._meta.fields:
        if field.related_model is root:
            yield parents + (field,)
        elif field.related_model:
            for chain in get_fk_chains(field.related_model, root, parents + (field,)):
                yield parents + chain


DIRECT_LINK = "{fk}::TEXT = current_setting('occupation.active_tenant')"
INDIRECT_LINK = "EXISTS (SELECT 1 FROM {related_table} WHERE {table_name}.{fk} = {related_table}.{pk})"


def get_policy_clauses(model, tenant_model):
    fields = set(field[0] for field in get_fk_chains(model, tenant_model))

    return [
        (DIRECT_LINK if field.related_model is tenant_model else INDIRECT_LINK).format(
            fk=db_column(field),
            pk=db_column(field.remote_field.target_field),
            related_table=field.related_model._meta.db_table,
            table_name=model._meta.db_table,
        ) for field in fields
    ]


def db_column(field):
    return field.db_column or field.attname


def activate_tenant(tenant_id):
    connection.cursor().execute("SET occupation.active_tenant = %s", [tenant_id])
