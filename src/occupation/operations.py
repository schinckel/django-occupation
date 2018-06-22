from django.db import migrations

from .utils import disable_row_level_security, enable_row_level_security


class EnableRowLevelSecurity(migrations.operations.base.Operation):
    reduces_to_sql = True

    def __init__(self, model_name, *args, **kwargs):
        self.superuser = kwargs.pop('superuser', False)
        super(EnableRowLevelSecurity, self).__init__(*args, **kwargs)
        self.model_name = model_name

    def database_forwards(self, app_label, schema_editor, from_state, to_state):
        enable_row_level_security(app_label, self.model_name, apps=to_state.apps, superuser=self.superuser)

    def database_backwards(self, app_label, schema_editor, from_state, to_state):
        disable_row_level_security(app_label, self.model_name, apps=to_state.apps, superuser=self.superuser)

    def state_forwards(self, app_label, state):
        pass

    def state_backwards(self, app_label, state):
        pass
