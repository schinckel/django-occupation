from __future__ import unicode_literals

from django.urls import path
from django.contrib import admin
# from django.contrib.auth.views import login, logout_then_login
from django.db import connection
from django.http import HttpResponse
from django.shortcuts import render

# from boardinghouse.schema import activate_schema
# import boardinghouse.contrib.demo.urls

admin.autodiscover()


def echo_schema(request):
    data = ""
    if request.GET:
        data = "\n" + "\n".join("{0!s}={1!s}".format(*x) for x in request.GET.items())
    return HttpResponse('{0!s}'.format(request.session.get('active_tenant')) + data)


def change_schema_view(request):
    return render(request, 'occupation/change_tenant.html', {})


def sql_injection(request):
    # Yes, this is an SQL injection view.
    connection.cursor().execute(request.GET.get('sql'))


urlpatterns = [
    path('', echo_schema),
    path('sql/', sql_injection),
    path('change/', change_schema_view),
    # url(r'^login/$', login, {'template_name': 'admin/login.html'}, name='login'),
    # url(r'^logout/$', logout_then_login, name='logout'),
    # url(r'^demo/', include(boardinghouse.contrib.demo.urls.urlpatterns)),
    path('admin/', admin.site.urls),
]
