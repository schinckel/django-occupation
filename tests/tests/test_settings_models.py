from django.test import TestCase

from boardinghouse.schema import is_shared_model

from ..models import SettingsSharedModel, SettingsPrivateModel


class TestSettingsModels(TestCase):
    def test_model_in_shared_models_is_shared(self):
        self.assertTrue(is_shared_model(SettingsSharedModel))

    def test_model_in_private_models_is_not_shared(self):
        self.assertFalse(is_shared_model(SettingsPrivateModel))
