from django.db.models.signals import post_save
# from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import Calendar
from clubs.models import Club

@receiver(post_save, sender=Club)
def create_calendar(sender, instance, created, **kwargs):
    if created:
        Calendar.objects.create(user=instance)
