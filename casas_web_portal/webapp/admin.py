from django.contrib import admin
from django.contrib.admin import SimpleListFilter
from django.utils.translation import gettext_lazy as _

# Register your models here.
from .models import Country, Organization, User, Job

class UserFilter(SimpleListFilter):
    """Filter to use with User model"""

    title = _("User")
    parameter_name = "user"

    def lookups(self, request, model_admin):
        if request.user.is_superuser:
            users = User.objects.all()
        else:
            users = [request.user]
        return [(b.id, b.username) for b in users]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(user__id__exact=self.value())


class OrganizationJobFilter(SimpleListFilter):
    """"""

    title = _("Organization")
    parameter_name = "orga"

    def lookups(self, request, model_admin):
        if request.user.is_superuser:
            orgas = Organization.objects.all()
        else:
            orgas = [request.user.organization]
        return [(b.id, b.username) for b in orgas]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(user__organization__id__exact=self.value())


class JobAdmin(admin.ModelAdmin):
    list_filter = [UserFilter, OrganizationJobFilter]
    search_fields = ("name", "model", "weather")


admin.site.register(Country)
admin.site.register(Organization)
admin.site.register(User)
admin.site.register(Job)