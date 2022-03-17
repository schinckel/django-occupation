from typing import Callable

from django.contrib.auth.models import AbstractBaseUser
from django.contrib.sessions.backends.base import SessionBase as Session
from django.db import connection
from django.http import HttpRequest, HttpResponse, HttpResponseForbidden
from django.shortcuts import redirect
from django.utils.translation import ugettext as _

from occupation.exceptions import Forbidden
from occupation.models import AbstractBaseTenant
from occupation.signals import session_tenant_changed
from occupation.utils import activate_tenant, get_tenant_model

TENANT_CHANGED = _("Tenant changed to %(active_tenant)s")
TENANT_CLEARED = _("Tenant deselected")
UNABLE_TO_CHANGE_TENANT = _("You may not select that tenant")

Tenant = get_tenant_model()


def clear_tenant(session: Session) -> None:
    session.pop("active_tenant", None)
    session.pop("active_tenant_name", None)


def set_tenant(session: Session, tenant: AbstractBaseTenant) -> None:
    session.update({"active_tenant": tenant.pk, "active_tenant_name": tenant.name})


def select_tenant(request: HttpRequest, tenant: str) -> None:
    """
    Ensure that the request/user is allowed to select this tenant,
    and then set that in the session.

    Does not actually activate the tenant.
    """
    session: Session = request.session
    user: AbstractBaseUser = request.user

    # Clear the tenant (deselect)
    if not tenant:
        clear_tenant(session)
        return

    # Clear the tenant if we have a non-authenticated user, and raise an exception,
    # because non-authenticated users may not switch tenants?
    if not user.is_authenticated:
        clear_tenant(session)
        raise Forbidden()

    # If no change, don't hit the database.
    if tenant == str(session.get("active_tenant")):
        return

    # Can this user view this tenant?
    try:
        tenant_instance: AbstractBaseTenant = user.visible_tenants.get(pk=tenant)
    except Tenant.DoesNotExist:
        raise Forbidden()
    else:
        set_tenant(session, tenant_instance)
        session_tenant_changed.send(sender=request, tenant=tenant_instance, user=user, session=session)


def SelectTenant(get_response: Callable) -> Callable:
    def middleware(request: HttpRequest) -> HttpResponse:
        try:
            if request.path.startswith("/__change_tenant__/"):
                select_tenant(request, request.path.split("/")[2])
                if request.session.get("active_tenant"):
                    return HttpResponse(TENANT_CHANGED % request.session)
                return HttpResponse(TENANT_CLEARED)
            elif request.GET.get("__tenant") is not None:
                select_tenant(request, request.GET["__tenant"])
                data = request.GET.copy()
                data.pop("__tenant")
                if request.method == "GET":
                    if data:
                        return redirect(request.path + "?" + data.urlencode())
                    return redirect(request.path)
                request.GET = data
            elif "HTTP_X_CHANGE_TENANT" in request.META:
                select_tenant(request, request.META["HTTP_X_CHANGE_TENANT"])
        except Forbidden:
            return HttpResponseForbidden(UNABLE_TO_CHANGE_TENANT)

        return get_response(request)

    return middleware


def ActivateTenant(get_response: Callable) -> Callable:
    def middleware(request: HttpRequest) -> HttpResponse:
        # Should we put this into the one query?
        if request.user.is_authenticated and request.user.pk:
            connection.cursor().execute("SET occupation.user_id = %s", [request.user.pk])
        activate_tenant(request.session.get("active_tenant", ""))
        return get_response(request)

    return middleware
