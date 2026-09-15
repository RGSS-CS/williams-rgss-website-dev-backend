from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from .models import STUCO, Announcements

# Reuse the same revalidation helper the management app uses, rather than
# duplicating the requests.post() logic here.
from management.signals import revalidate_frontend_tag


@receiver(post_save, sender=STUCO)
@receiver(post_delete, sender=STUCO)
@receiver(post_save, sender=Announcements)
@receiver(post_delete, sender=Announcements)
def on_club_change(sender, instance, **kwargs):
    revalidate_frontend_tag("stuco-settings")