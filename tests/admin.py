from django.contrib import admin

from .models import RelatedModel, DistinctModel

admin.site.register(RelatedModel)
admin.site.register(DistinctModel)
