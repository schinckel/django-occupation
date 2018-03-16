from django.apps import AppConfig
from django.core.checks import Error, Warning, register


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


@register('settings')
def check_middleware_installed_correctly(app_configs=None, **kwargs):
    # Installed after SessionMiddleware.
    Error
    return []


@register('settings')
def check_context_manager_installed(app_configs=None, **kwargs):
    # Warning if not.
    Warning
    return []


@register('settings')
def check_installed_before_admin(app_configs=None, **kwargs):
    # Warning if not, as we can't override templates.
    Warning
    return []


def set_dummy_active_tenant(sender, connection, **kwargs):
    connection.cursor().execute("SET occupation.active_tenant = ''")
