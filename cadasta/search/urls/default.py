from django.conf.urls import include, url

from ..views import default

urls = [
    url(
        r'^search/$',
        default.SearchResults.as_view(),
        name='results'),
]

urlpatterns = [
    url(
        r'^organizations/(?P<organization>[-\w]+)/projects/'
        '(?P<project>[-\w]+)/',
        include(urls)),
]
