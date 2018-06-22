def tenants(request):
    if request.user.is_anonymous:
        return {}

    return {
        'active_tenant': request.session.get('active_tenant'),
        'tenant_choices': request.user.visible_tenants.values_list('pk', 'name'),
        'visible_tenants': request.user.visible_tenants,
    }
