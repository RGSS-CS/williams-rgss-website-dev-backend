from django.apps import AppConfig


class GalleriesConfig(AppConfig):
    name = 'galleries'

    verbose_name = 'Media'

    def ready(self):
        from . import signals