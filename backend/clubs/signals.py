from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from .models import Club, ClubWhyJoin, ClubAnnouncement

# Reuse the same revalidation helper the management app uses, rather than
# duplicating the requests.post() logic here.
from management.signals import revalidate_frontend_tag


@receiver(post_save, sender=Club)
@receiver(post_delete, sender=Club)
@receiver(post_save, sender=ClubWhyJoin)
@receiver(post_delete, sender=ClubWhyJoin)
@receiver(post_save, sender=ClubAnnouncement)
@receiver(post_delete, sender=ClubAnnouncement)
def on_club_change(sender, instance, **kwargs):
    revalidate_frontend_tag("clubs")
