from django.apps import AppConfig

class ClubsConfig(AppConfig):
    name = 'clubs'
    verbose_name = 'School Activities'

    def ready(self):
        from clubs import signals
