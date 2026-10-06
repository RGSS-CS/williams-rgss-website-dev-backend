from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from .models import Stuco, Announcements

@receiver(post_save, sender=Stuco)
@receiver(post_delete, sender=Stuco)
@receiver(post_save, sender=Announcements)
@receiver(post_delete, sender=Announcements)
def on_club_change(sender, instance=None, **kwargs):
    from management.signals import revalidate_frontend_tag

    revalidate_frontend_tag("stuco-settings")
