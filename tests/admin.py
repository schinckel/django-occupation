from django.contrib import admin

from .models import DistinctModel, RelatedModel, RestrictedModel

admin.site.register(RelatedModel)
admin.site.register(DistinctModel)
admin.site.register(RestrictedModel)
