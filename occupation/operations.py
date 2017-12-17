from django.db import migrations

ENABLE_RLS = 'ALTER TABLE {table_name} ENABLE ROW LEVEL SECURITY'
ALLOW_ACCESS = '''
CREATE POLICY access_tenant_data ON {table_name}
USING (tenant_id = current_setting('occupation.active_tenant')::INTEGER)
'''

class EnableRowLevelSecurity(migrations.Operation):
    def __init__(self, *args, **kwargs):
        super(EnableRowLevelSecurity, self).__init__(*args, **kwargs)

    def database_forwards(self, app_label, state):
        pass