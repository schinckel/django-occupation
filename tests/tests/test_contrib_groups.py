from django.test import TestCase, modify_settings


class TestContribGroups(TestCase):
    @modify_settings()
    def test_loading_app_file(self):
        from django.conf import settings

        from boardinghouse.contrib import groups
        from boardinghouse.contrib.groups.apps import GroupsConfig

        config = GroupsConfig('boardinghouse.contrib.groups', groups)
        config.ready()

        self.assertTrue('auth.groups' in settings.PRIVATE_MODELS)
        settings.PRIVATE_MODELS.remove('auth.groups')
