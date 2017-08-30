from django.apps import AppConfig


class UsersConfig(AppConfig):
    """
    App config for users app.
    """
    name = 'users'

    def ready(self):
        from . import signals  # noqa
