import core.views.generic as generic
from core.mixins import LoginPermissionRequiredMixin
from organization.views import mixins
from party.views.mixins import PartyQuerySetMixin


class SearchResults(PartyQuerySetMixin,
                    LoginPermissionRequiredMixin,
                    mixins.ProjectAdminCheckMixin,
                    generic.ListView):
    template_name = 'search/search_results.html'
    permission_required = 'party.list'
    permission_filter_queryset = (
        'party.view', 'spatial_unit.view',
        'tenure_rel.view', 'resource.view')

    def get_queryset(self):
        self.proj = self.get_project()
        parties = self.proj.parties.all()
        spatial_units = self.proj.spatial_units.all()
        tenure_rels = self.proj.tenure_relationships.all()
        # if (
        #     hasattr(self, 'no_jsonattrs_in_queryset') and
        #     self.no_jsonattrs_in_queryset
        # ):
        #     parties = parties.only('id', 'name', 'type', 'project')
        return parties

    def get_perms_objects(self):
        return [self.get_project()]
