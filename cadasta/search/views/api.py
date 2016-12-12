import requests
import json

from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from tutelary.mixins import APIPermissionRequiredMixin

from organization.views.mixins import ProjectMixin
from spatial.models import SpatialUnit
from party.models import Party, TenureRelationship
from resources.models import Resource


class Search(APIPermissionRequiredMixin,
             ProjectMixin,
             APIView):

    permission_required = 'project.view'

    def get_object(self, queryset=None):
        return self.get_project()

    def get_perms_objects(self):
        return [self.get_project()]

    def get(self, request, *args, **kwargs):
        query = request.query_params.get('q')

        results = []

        if query:
            # Access ES search API
            body = {'query': {'simple_query_string': {
                'default_operator': 'and',
                'query': query,
            }}}
            api = (
                settings.ES_SCHEME + '://' + settings.ES_HOST + ':' +
                settings.ES_PORT
            )
            r = requests.post(
                api + '/' + kwargs['project'] + '/_search',
                data=json.dumps(body, sort_keys=True),
            )

            # Parse and translate search results
            for result in r.json()['hits']['hits']:
                rec_type = result['_type']
                id = result['_id']
                model = {
                    'location': SpatialUnit,
                    'party': Party,
                    'tenure_rel': TenureRelationship,
                    'resource': Resource,
                }[rec_type]
                record = model.objects.get(id=id)
                # TODO: Perform Tutelary permissions checking
                results.append([
                    record.ui_class_name,
                    '<a href="{}">{}</a>'.format(
                        record.ui_detail_url,
                        record.name,
                    ),
                ])

        return Response({'results': results})
