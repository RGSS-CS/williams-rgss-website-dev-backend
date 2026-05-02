from django.apps import AppConfig


class CalendarsConfig(AppConfig):
    name = 'calendars'

    def ready(self):
        from calendars import signals