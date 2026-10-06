from django.apps import AppConfig


class ManagementConfig(AppConfig):
    name = 'management'
    verbose_name = 'Site Management'

    def ready(self):
        from . import signals
        signals.on_post_migrate(sender=self, app_config=self)
