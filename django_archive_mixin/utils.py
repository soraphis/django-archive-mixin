from distutils.version import StrictVersion

import django
from django.db import models
from django.utils import timezone
from datetime import timedelta


def get_field_by_name(model, field):
    """
    Retrieve a field instance from a model by its name.
    """
    field_dict = {x.name: x for x in model._meta.get_fields()}

    return field_dict[field]


def cascade_archive(inst_or_qs, using, keep_parents=False):
    """
    Return collector instance that has marked ArchiveMixin instances for
    archive (i.e. update) instead of actual delete.

    Arguments:
        inst_or_qs (models.Model or models.QuerySet): the instance(s) that
            are to be deleted.
        using (db connection/router): the db to delete from.
        keep_parents (bool): defaults to False.  Determine if cascade is true.

    Returns:
        models.deletion.Collector: this is a standard Collector instance but
            the ArchiveMixin instances are in the fields for update list.
    """
    from .mixins import ArchiveMixin

    if not isinstance(inst_or_qs, models.QuerySet):
        instances = [inst_or_qs]
    else:
        instances = inst_or_qs

    deleted_ts = timezone.now()

    # The collector will iteratively crawl the relationships and
    # create a list of models and instances that are connected to
    # this instance.
    collector = models.deletion.Collector(using=using)
    if StrictVersion(django.get_version()) < StrictVersion('1.9.0'):
        collector.collect(instances)
    else:
        collector.collect(instances, keep_parents=keep_parents)
    collector.sort()

    for model, instances in list(collector.data.items()):
        # remove archive mixin models from the delete list and put
        # them in the update list.  If we do this, we can just call
        # the collector.delete method.
        inst_list = list(instances)

        if issubclass(model, ArchiveMixin):
            updated_inst_list = []
            for instance in inst_list:
                if instance.deleted is None:
                    updated_inst_list.append(instance)

            deleted_field = get_field_by_name(model, 'deleted')
            collector.add_field_update(
                deleted_field, deleted_ts, updated_inst_list)

            del collector.data[model]

    for i, qs in enumerate(collector.fast_deletes):
        # make sure that we do archive on fast deletable models as
        # well.
        model = qs.model

        if issubclass(model, ArchiveMixin):
            qs2 = qs.filter(deleted__isnull=True)
            deleted_field = get_field_by_name(model, 'deleted')
            collector.add_field_update(deleted_field, deleted_ts, qs2)

            collector.fast_deletes[i] = qs.none()

    return collector


def cascade_unarchive(inst_or_qs, using, deleted_date, keep_parents=False):
    """
    Return collector instance that has marked ArchiveMixin instances for
    unarchive (i.e. update).

    Arguments:
        inst_or_qs (models.Model or models.QuerySet): the instance(s) that
            are to be deleted.
        using (db connection/router): the db to delete from.
        keep_parents (bool): defaults to False.  Determine if cascade is true.

    Returns:
        models.deletion.Collector: this is a standard Collector instance but
            the ArchiveMixin instances are in the fields for update list.
    """
    from .mixins import ArchiveMixin

    if not isinstance(inst_or_qs, models.QuerySet):
        instances = [inst_or_qs]
    else:
        instances = inst_or_qs

    # The collector will iteratively crawl the relationships and
    # create a list of models and instances that are connected to
    # this instance.
    collector = models.deletion.Collector(using=using)
    if StrictVersion(django.get_version()) < StrictVersion('1.9.0'):
        collector.collect(instances)
    else:
        collector.collect(instances, keep_parents=keep_parents)
    collector.sort()

    for model, instances in list(collector.data.items()):
        # remove archive mixin models from the delete list and put
        # them in the update list.  If we do this, we can just call
        # the collector.delete method.
        inst_list = list(instances)

        if issubclass(model, ArchiveMixin):
            updated_inst_list = []
            for instance in inst_list:
                if instance.deleted is not None and abs(
                        (deleted_date - instance.deleted).total_seconds()) < 60:
                    updated_inst_list.append(instance)

            deleted_field = get_field_by_name(model, 'deleted')
            collector.add_field_update(
                deleted_field, None, updated_inst_list)

        del collector.data[model]

    td = timedelta(seconds=60)
    for i, qs in enumerate(collector.fast_deletes):
        # make sure that we do archive on fast deletable models as
        # well.
        model = qs.model

        if issubclass(model, ArchiveMixin):
            qs2 = qs.filter(deleted__gte=deleted_date-td, deleted__lte=deleted_date+td)
            deleted_field = get_field_by_name(model, 'deleted')
            collector.add_field_update(deleted_field, None, qs2)

        collector.fast_deletes[i] = qs.none()

    return collector
