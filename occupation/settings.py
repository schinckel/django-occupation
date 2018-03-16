OCCUPATION_TENANT_MODEL = 'occupation.Tenant'
"""
The model that will store the tenant objects.

This should be a subclass of :class:`tenant.models.AbstractTenant`, or
expose the same methods.
"""


DATABASE_OWNER_ROLE = 'owner'
"""
The postgres user that will own the database tables.

This must be
"""