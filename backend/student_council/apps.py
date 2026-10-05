from django.apps import AppConfig


class StudentCouncilConfig(AppConfig):
    name = 'student_council'
    verbose_name = 'Student Council'

    def ready(self):
        from . import signals
        signals.on_club_change(sender=self)
