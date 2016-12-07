import core.views.generic as generic
from core.mixins import LoginPermissionRequiredMixin
from organization.views import mixins
from party.views.mixins import PartyQuerySetMixin

from .. import forms


# Does this need to be a project detail view like dashboard?
class SearchResults(LoginPermissionRequiredMixin,
                    mixins.ProjectAdminCheckMixin,
                    mixins.ProjectMixin,
                    generic.DetailView):
    template_name = 'search/search_results.html'
    # Do we need a 'record' permission view?
    # Or does it make sense that if a person can view parties,
    # they can view anything?
    permission_required = 'party.view'
    form_class = forms.SearchForm
    # permission_filter_queryset = (
    #     'party.view', 'spatial_unit.view',
    #     'tenure_rel.view', 'resource.view')

    def get_object(self, queryset=None):
        return self.get_project()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        search_results = {
              "took": 63,
              "timed_out": False,
              "_shards": {
                "total": 5,
                "successful": 5,
                "failed": 0
              },
              "hits": {
                "total": 1000,
                "max_score": "null",
                "hits": [{
                  "_index": "bank",
                  "_type": "party",
                  "_id": "0",
                  "sort": [0],
                  "_score": 'null',
                  "_source": {
                    "party_name": "Big Bird",
                    "type": "CB"
                   }
                }, {
                  "_index": "bank",
                  "_type": "party",
                  "_id": "1",
                  "sort": [1],
                  "_score": "null",
                  "_source": {
                    "party_name": "Miss Piggy",
                    "type": "CB"
                   }
                },
                ]
              }
            }

        context['search_total'] = search_results['hits']['total']
        context['search_terms'] = 'foo bar'
        context['search_results'] = []
        for result in search_results['hits']['hits']:
            context['search_results'].append({
                'id': result['_id'],
                'source': {
                    'entity_name': result['_type'].capitalize(),
                    'entity_type': result['_source']['type'],
                    'required_fields': [{
                        'label': 'Name of Party',
                        'body': result['_source']['party_name']
                        }],
                    'additional_fields': ['Location Notes']
                }
            })
            # context['entity_name'] = result['_type'].uppercase()
            # context['entity_type'] = results['_source']['type']
            # context['required_fields'] = ['Name of Location']
            # context['additional_fields'] = ['Location Notes']
        return context

    # def get_perms_objects(self):
    #     return [self.get_project()]
