from django.apps import AppConfig
from django.db.models.signals import post_migrate


class ManagementConfig(AppConfig):
    name = 'management'
    verbose_name = 'Site Management'

    def ready(self):
        from .signals import on_post_migrate
        post_migrate.connect(on_post_migrate, sender=self)