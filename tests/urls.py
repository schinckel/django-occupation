from __future__ import unicode_literals

from django.conf.urls import include, url
from django.contrib import admin
# from django.contrib.auth.views import login, logout_then_login
from django.db import connection
from django.http import HttpResponse
from django.shortcuts import render
import django

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


def aware_objects_view(request):
    from .models import AwareModel
    obj = AwareModel.objects.all()[0]
    return HttpResponse(obj.name)


def sql_injection(request):
    # Yes, this is an SQL injection view.
    connection.cursor().execute(request.GET.get('sql'))


def activate_schema_view(request, schema):
    # Don't do this.
    # activate_schema(schema)
    return HttpResponse(schema)

urlpatterns = [
    url(r'^$', echo_schema),
    url(r'^sql/$', sql_injection),
    url(r'^change/$', change_schema_view),
    url(r'^aware/$', aware_objects_view),
    # url(r'^login/$', login, {'template_name': 'admin/login.html'}, name='login'),
    # url(r'^logout/$', logout_then_login, name='logout'),
    url(r'^bad/activate/schema/(.*)/$', activate_schema_view, name='bad-view'),
    # url(r'^demo/', include(boardinghouse.contrib.demo.urls.urlpatterns)),
]

if django.VERSION < (1, 9):
    urlpatterns.append(url(r'^admin/', include(admin.site.urls)))
else:
    urlpatterns.append(url(r'^admin/', include(admin.site.urls[:2], namespace='admin')))
