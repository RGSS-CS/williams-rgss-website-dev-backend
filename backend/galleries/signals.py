from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Photos, MassImport

# Reuse the same revalidation helper the management app uses, rather than
# duplicating the requests.post() logic here.
from management.signals import revalidate_frontend_tag

@receiver(post_save, sender=MassImport)
def execute_unzip():
    

@receiver(post_save, sender=Photos)
@receiver(post_delete, sender=Photos)
def on_media_change(sender, instance, **kwargs):
    revalidate_frontend_tag("gallery-photos")
