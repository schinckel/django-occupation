from django.dispatch import Signal

tenant_created = Signal(providing_args=['tenant'])
tenant_deleted = Signal(providing_args=['tenant'])

tenant_pre_activate = Signal(providing_args=['tenant'])
tenant_post_activate = Signal(providing_args=['tenant'])

session_requesting_tenant_change = Signal(providing_args=['user', 'tenant', 'session'])
session_tenant_changed = Signal(providing_args=['user', 'tenant', 'session'])

find_tenants = Signal(providing_args=['tenant'])
