from django.apps import AppConfig

class ClubsConfig(AppConfig):
    name = 'clubs'

    def ready(self):
        from . import signals  # noqa: F401 — registers post_save/post_delete receivers