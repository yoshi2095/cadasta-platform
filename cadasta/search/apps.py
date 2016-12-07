from django.apps import AppConfig


class SearchConfig(AppConfig):
    name = 'search'
    verbose_name = 'Search'

    def ready(self):
        import search.signals
