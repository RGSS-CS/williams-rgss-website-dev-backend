from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from .models import Club, ClubAnnouncement


@receiver(post_save, sender=Club)
@receiver(post_delete, sender=Club)
@receiver(post_save, sender=ClubAnnouncement)
@receiver(post_delete, sender=ClubAnnouncement)
def on_club_change(sender, instance=None, **kwargs):
    from management.signals import revalidate_frontend_tag

    revalidate_frontend_tag("clubs")
