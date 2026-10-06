from django.apps import AppConfig


class ManagementConfig(AppConfig):
    name = 'management'
    verbose_name = 'Site Management'

    def ready(self):
        from management import signals
