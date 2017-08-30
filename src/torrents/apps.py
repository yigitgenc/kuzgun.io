from django.apps import AppConfig


class TorrentsConfig(AppConfig):
    """
    App config for torrents app.
    """
    name = 'torrents'

    def ready(self):
        from . import signals  # noqa

