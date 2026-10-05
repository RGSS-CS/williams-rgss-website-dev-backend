from django.apps import AppConfig

class ClubsConfig(AppConfig):
    name = 'clubs'
    verbose_name = 'School Activities'

    def ready(self):
        from . import signals
        signals.on_club_change(sender=self)
