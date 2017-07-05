from django.apps import AppConfig


class TorrentsConfig(AppConfig):
    name = 'torrents'

    def ready(self):
        from . import signals  # noqa

