from django.db import models

from django_archive_mixin.mixins import ArchiveMixin


class BaseModel(models.Model):
    name = models.CharField(max_length=100, blank=True, null=True)


class NullRelatedModel(models.Model):
    nullable_base = models.ForeignKey(BaseModel, blank=True, null=True, on_delete=models.CASCADE, related_name="nulls")


class BaseArchiveModel(ArchiveMixin, models.Model):
    name = models.CharField(max_length=100, blank=True, null=True)


class RelatedModel(models.Model):
    base = models.ForeignKey(BaseArchiveModel, on_delete=models.CASCADE, related_name="relateds")
    null_base = models.ForeignKey(BaseArchiveModel, blank=True, null=True, on_delete=models.CASCADE, related_name="relateds2")
    set_null_base = models.ForeignKey(
        BaseArchiveModel,
        blank=True, null=True, on_delete=models.deletion.SET_NULL, related_name="relateds3")
    set_default_base = models.ForeignKey(
        BaseArchiveModel,
        blank=True, null=True, on_delete=models.deletion.SET_DEFAULT, default=None, related_name="relateds4")


class RelatedCousinModel(models.Model):
    related = models.ForeignKey(RelatedModel, on_delete=models.CASCADE, related_name="related_cousins")
    null_related = models.ForeignKey(RelatedModel, blank=True, null=True, on_delete=models.CASCADE, related_name="related_cousins2")
    set_null_related = models.ForeignKey(
        RelatedModel,
        blank=True, null=True, on_delete=models.deletion.SET_NULL, related_name="related_cousins3")
    set_default_related = models.ForeignKey(
        RelatedModel,
        blank=True, null=True, on_delete=models.deletion.SET_DEFAULT, default=None, related_name="related_cousins4")


class RelatedArchiveModel(ArchiveMixin, models.Model):
    base = models.ForeignKey(BaseArchiveModel, on_delete=models.CASCADE, related_name="related_archives")
    null_base = models.ForeignKey(BaseArchiveModel, blank=True, null=True, on_delete=models.CASCADE, related_name="related_archives2")
    set_null_base = models.ForeignKey(
        BaseArchiveModel,
        blank=True, null=True, on_delete=models.deletion.SET_NULL, related_name="related_archives3")
    set_default_base = models.ForeignKey(
        BaseArchiveModel,
        blank=True, null=True, on_delete=models.deletion.SET_DEFAULT, default=None, related_name="related_archives4")


class RelatedCousinArchiveModel(ArchiveMixin, models.Model):
    related = models.ForeignKey(RelatedArchiveModel, on_delete=models.CASCADE, related_name="related_c_archives")
    null_related = models.ForeignKey(
        RelatedArchiveModel, blank=True, null=True, on_delete=models.CASCADE, related_name="related_c_archives2")
    null_related = models.ForeignKey(
        RelatedArchiveModel,
        blank=True, null=True, on_delete=models.deletion.SET_NULL, related_name="related_c_archives3")
    set_default_related = models.ForeignKey(
        RelatedArchiveModel,
        blank=True, null=True, on_delete=models.deletion.SET_DEFAULT, default=None, related_name="related_c_archives4")

