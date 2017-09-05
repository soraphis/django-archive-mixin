from django.contrib.admin import SimpleListFilter
from django_archive_mixin.mixins import ArchiveMixin

def really_delete(modeladmin, request, queryset):
    for q in queryset.all():
        if not isinstance(q, ArchiveMixin): continue
        q.really_delete()

def get_ArchivedFilter(for_class):
    
    class ArchivedFilter(SimpleListFilter):
        title = "Archived"
        parameter_name = "deleted"

        def lookups(self, request, model_admin):
            return [("non", "Non-Archive"), ("arc", "Archive")]

        def queryset(self, request, queryset):
            if self.value() == "non":
                return queryset
            if self.value() == "arc":
                return for_class.objects.deleted
            return for_class.all_objects.all()
    
    return ArchivedFilter
