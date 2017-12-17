from django.db import migrations

from .utils import enable_row_level_security


class EnableRowLevelSecurity(migrations.Operation):
    def __init__(self, *args, **kwargs):
        super(EnableRowLevelSecurity, self).__init__(*args, **kwargs)

    def database_forwards(self, app_label, state):
        enable_row_level_security()
