from django.db import models

from occupation.base import BaseRelatedModel


class RelatedModel(models.Model):
    tenant = models.ForeignKey("occupation.Tenant", on_delete=models.CASCADE)
    name = models.CharField(max_length=10, unique=True)
    status = models.BooleanField(default=False)
    factor = models.PositiveSmallIntegerField(default=7)


class DistinctModel(models.Model):
    name = models.CharField(max_length=10, unique=True)
    status = models.BooleanField(default=False)


class RestrictedModel(BaseRelatedModel):
    name = models.CharField(max_length=10, unique=True)
