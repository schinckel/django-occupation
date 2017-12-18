from django.db import models


class AwareModel(models.Model):
    name = models.CharField(max_length=10, unique=True)
    status = models.BooleanField(default=False)
    factor = models.PositiveSmallIntegerField(default=7)


class NaiveModel(models.Model):
    name = models.CharField(max_length=10, unique=True)
    status = models.BooleanField(default=False)


# The existence of this model, although it may not have tests
# that apply to it, is enough to trigger infinite recursion if
# a check for self-referencing models is not made in is_shared_model()
class SelfReferentialModel(models.Model):
    name = models.CharField(max_length=10, unique=True)
    parent = models.ForeignKey('tests.SelfReferentialModel',
                               on_delete=models.CASCADE,
                               related_name='children',
                               null=True, blank=True)


# If you have two models that _only_ have foreign keys, and they happen
# to include references to one another, then you could get an infinite
# recursion. However, I can't see that this model structure makes sense.
class CoReferentialModelA(models.Model):
    name = models.CharField(max_length=10, unique=True)
    other = models.ForeignKey('tests.CoReferentialModelB',
                              on_delete=models.CASCADE,
                              related_name='model_a',
                              null=True, blank=True)


class CoReferentialModelB(models.Model):
    name = models.CharField(max_length=10, unique=True)
    other = models.ForeignKey('tests.CoReferentialModelA',
                              on_delete=models.CASCADE,
                              related_name='model_b',
                              null=True, blank=True)


# We do prefix testing to determine if a model is shared.
class ModelA(models.Model):
    pass


class ModelB(models.Model):
    pass


class ModelBPrefix(models.Model):
    model_a = models.ManyToManyField(ModelA)


class SettingsSharedModel(models.Model):
    pass


class SettingsPrivateModel(models.Model):
    pass


class ViewBackedModel(models.Model):
    class Meta:
        managed = False
