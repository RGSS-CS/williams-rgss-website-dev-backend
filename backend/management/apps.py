from django.apps import AppConfig


class ManagementConfig(AppConfig):
    name = 'management'

    def ready(self):
        from django.db.models.signals import post_migrate
        from .signals import on_post_migrate
        post_migrate.connect(on_post_migrate, sender=self)
        

