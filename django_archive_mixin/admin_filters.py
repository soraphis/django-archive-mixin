from django.contrib.admin import SimpleListFilter

class ArchivedFilter(SimpleListFilter):
    title = "Archived"
    parameter_name = "deleted"

    def lookups(self, request, model_admin):
        return [("non", "Non-Archive"), ("arc", "Archive")]

    def queryset(self, request, queryset):
        if self.value() == "non":
            return queryset
        if self.value() == "arc":
            return WaitListEntry.objects.deleted
        return WaitListEntry.all_objects.all()
