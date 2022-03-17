from django.dispatch import Signal

tenant_created = Signal()
tenant_deleted = Signal()

tenant_pre_activate = Signal()
tenant_post_activate = Signal()

session_requesting_tenant_change = Signal()
session_tenant_changed = Signal()

find_tenants = Signal()
