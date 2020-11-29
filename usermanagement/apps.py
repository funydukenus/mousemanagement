from django.apps import AppConfig


class UsermanagementConfig(AppConfig):
    name = 'usermanagement'

    def ready(self):
        # Makes sure all signal handlers are connected
        from usermanagement import handlers  # noqa
