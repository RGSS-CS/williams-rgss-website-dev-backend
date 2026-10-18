from django.apps import AppConfig


class StudentCouncilConfig(AppConfig):
    name = 'student_council'
    verbose_name = 'Organizational Settings'

    def ready(self):
        from . import signals
