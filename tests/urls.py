from __future__ import unicode_literals

import json

from django.apps import apps
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


def get_list(request, model):
    model_class = apps.get_model('tests', model)
    return HttpResponse(json.dumps(list(model_class.objects.values('pk', 'name'))), content_type='application/json')


def get_object(request, model, pk):
    model_class = apps.get_model('tests', model)
    return HttpResponse('{name}'.format(model_class.objects.get(pk=pk)))


urlpatterns = [
    path('', echo_schema),
    path('sql/', sql_injection),
    path('change/', change_schema_view),
    path('get/<model>/', get_list),
    path('get/<model>/<int:pk>/', get_object),
    # url(r'^login/$', login, {'template_name': 'admin/login.html'}, name='login'),
    # url(r'^logout/$', logout_then_login, name='logout'),
    # url(r'^demo/', include(boardinghouse.contrib.demo.urls.urlpatterns)),
    path('admin/', admin.site.urls),
]
