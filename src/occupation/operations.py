from django.db import migrations
from django.db.backends.base.schema import (
    BaseDatabaseSchemaEditor as SchemaEditor,
)
from django.db.migrations.state import ProjectState

from occupation.utils import (
    disable_row_level_security, enable_row_level_security,
)


class EnableRowLevelSecurity(migrations.operations.base.Operation):
    reduces_to_sql = True

    def __init__(self, model_name: str, *args, **kwargs) -> None:
        self.superuser = kwargs.pop('superuser', False)
        super(EnableRowLevelSecurity, self).__init__(*args, **kwargs)
        self.model_name = model_name

    def database_forwards(
        self, app_label: str,
        schema_editor: SchemaEditor,
        from_state: ProjectState,
        to_state: ProjectState
    ) -> None:
        enable_row_level_security(app_label, self.model_name, apps=to_state.apps, superuser=self.superuser)

    def database_backwards(
        self, app_label: str,
        schema_editor: SchemaEditor,
        from_state: ProjectState,
        to_state: ProjectState
    ) -> None:
        disable_row_level_security(app_label, self.model_name, apps=to_state.apps, superuser=self.superuser)

    def state_forwards(self, app_label: str, state: ProjectState) -> None:  # pragma: no cover
        pass

    def state_backwards(self, app_label: str, state: ProjectState) -> None:  # pragma: no cover
        pass
