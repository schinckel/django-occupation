from copy import deepcopy

from django.conf import settings
from django.test import TestCase, modify_settings, override_settings

from occupation import apps


class TestSettings(TestCase):
    def test_all_settings(self):
        self.assertEqual([], apps.check_session_middleware_installed())
        self.assertEqual([], apps.check_middleware_installed_correctly())
        self.assertEqual([], apps.check_context_processor_installed())
        self.assertEqual([], apps.check_installed_before_admin())

    @modify_settings(MIDDLEWARE={'remove': apps.MIDDLEWARE})
    def test_middleware_missing(self):
        errors = apps.check_middleware_installed_correctly()
        self.assertEqual(2, len(errors))
        self.assertEqual('occupation.E002', errors[0].id)
        self.assertEqual('occupation.E002', errors[1].id)

    @modify_settings(MIDDLEWARE={'remove': ['django.contrib.sessions.middleware.SessionMiddleware']})
    def test_session_middleware_missing(self):
        errors = apps.check_session_middleware_installed()
        self.assertEqual(1, len(errors))
        self.assertEqual('occupation.E001', errors[0].id)

        self.assertEqual([], apps.check_middleware_installed_correctly())

    @modify_settings(MIDDLEWARE={
        'remove': apps.MIDDLEWARE,
        'append': apps.MIDDLEWARE[::-1],
    })
    def test_middleware_order_incorrect(self):
        errors = apps.check_middleware_installed_correctly()
        self.assertEqual(1, len(errors))
        self.assertEqual('occupation.E004', errors[0].id)

    @modify_settings(MIDDLEWARE={
        'remove': apps.MIDDLEWARE,
        'prepend': apps.MIDDLEWARE,
    })
    def test_middleware_before_session_middleware(self):
        errors = apps.check_middleware_installed_correctly()
        self.assertEqual(2, len(errors))
        self.assertEqual('occupation.E003', errors[0].id)
        self.assertEqual('occupation.E003', errors[1].id)

    @modify_settings(INSTALLED_APPS={
        'remove': 'occupation',
        'append': 'occupation',
    })
    def test_installed_before_admin(self):
        errors = apps.check_installed_before_admin()
        self.assertEqual(1, len(errors))
        self.assertEqual('occupation.W002', errors[0].id)

    @modify_settings(INSTALLED_APPS={
        'remove': 'django.contrib.admin',
    })
    def test_admin_not_installed(self):
        self.assertEqual([], apps.check_installed_before_admin())

    @modify_settings()
    def test_missing_context_manager(self):
        templates = deepcopy(settings.TEMPLATES)
        templates[0]['OPTIONS']['context_processors'].remove(apps.CONTEXT)
        with self.settings(TEMPLATES=templates):
            errors = apps.check_context_processor_installed()
            self.assertEqual(1, len(errors))
            self.assertEqual('occupation.W001', errors[0].id)

    @override_settings(TEMPLATES=[{
        'BACKEND': 'django.template.backends.jinja2.Jinja2',
    }])
    def test_context_processor_not_installed_but_using_jinja(self):
        errors = apps.check_context_processor_installed()
        self.assertEqual(0, len(errors))
