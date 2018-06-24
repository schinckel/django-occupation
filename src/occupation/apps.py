from django.apps import AppConfig
from django.core.checks import Error, Warning, register


MIDDLEWARE = [
    'occupation.middleware.SelectTenant',
    'occupation.middleware.ActivateTenant',
]

CONTEXT = 'occupation.context_processors.tenants'


class OccupationConfig(AppConfig):
    name = 'occupation'

    def ready(self):
        # Apply settings from defaults, if they have not been overridden.

        from occupation import settings as default_settings
        from django.conf import settings, global_settings

        for key in dir(default_settings):
            if key.isupper():
                value = getattr(default_settings, key)
                setattr(global_settings, key, value)
                if not hasattr(settings, key):
                    setattr(settings, key, value)

        # from . import receivers  # NOQA
        from django.db.backends.signals import connection_created
        connection_created.connect(set_dummy_active_tenant)

        from .admin import patch_admin
        patch_admin()


def session_middleware_index(settings):
    for i, middleware in enumerate(settings.MIDDLEWARE):
        if middleware.endswith('.SessionMiddleware'):
            return i


@register('settings')
def check_session_middleware_installed(app_configs=None, **kwargs):
    from django.conf import settings

    if session_middleware_index(settings) is None:
        return [Error(
            'It appears that no session middleware is installed.',
            hint="Add 'django.contrib.sessions.middleware.SessionMiddleware' to your MIDDLEWARE",
            id='occupation.E001',
        )]
    return []


@register('settings')
def check_middleware_installed_correctly(app_configs=None, **kwargs):
    from django.conf import settings

    errors = []

    session = session_middleware_index(settings)

    if session is not None:
        for middleware in MIDDLEWARE:
            if middleware not in settings.MIDDLEWARE:
                errors.append(
                    Error(
                        'The middleware "{}" is not installed.'.format(middleware),
                        id='occupation.E002',
                    )
                )
            elif settings.MIDDLEWARE.index(middleware) < session:
                errors.append(
                    Error(
                        'The occupation middleware "{}" is installed before the session middleware.'.format(
                            middleware
                        ),
                        id='occupation.E003',
                    )
                )

    try:
        if settings.MIDDLEWARE.index(MIDDLEWARE[1]) < settings.MIDDLEWARE.index(MIDDLEWARE[0]):
            errors.append(
                Error(
                    'The middleware "{1}" must be installed after "{0}".'.format(*MIDDLEWARE),
                    id='occupation.E004'
                )
            )
    except ValueError:
        pass

    return errors


@register('settings')
def check_context_processor_installed(app_configs=None, **kwargs):
    # Warning if not.
    from django.conf import settings

    errors = []

    for i, engine in enumerate(settings.TEMPLATES):
        if engine['BACKEND'] != 'django.template.backends.django.DjangoTemplates':
            continue
        if CONTEXT not in engine.get('OPTIONS', {}).get('context_processors', []):
            errors.append(Warning(
                'Missing context processor "{}"'.format(CONTEXT),
                hint="Add '{1}' to settings.TEMPLATES[{0}]['OPTIONS']['context_processors']".format(
                    i, CONTEXT
                ),
                id='occupation.W001',
            ))

    return errors


@register('settings')
def check_installed_before_admin(app_configs=None, **kwargs):
    from django.conf import settings

    # Warning if not, as we can't override templates.
    if 'django.contrib.admin' in settings.INSTALLED_APPS:
        if settings.INSTALLED_APPS.index('django.contrib.admin') < settings.INSTALLED_APPS.index('occupation'):
            return [
                Warning(
                    "'occupation' must be installed prior to 'django.contrib.admin', to allow overridding templates.",
                    id='occupation.W002'
                )
            ]
    return []


def set_dummy_active_tenant(sender, connection, **kwargs):
    connection.cursor().execute("SET occupation.active_tenant = ''")
