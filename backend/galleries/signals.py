from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db import transaction
from django_tasks import signals

from management.signals import revalidate_frontend_tag

from .models import Photos, MassImport
from .tasks import import_mass_upload

@receiver(post_save, sender=MassImport)
def execute_unzip(sender, instance, created, **kwargs):
    if not created:
        return

    transaction.on_commit(
        lambda: import_mass_upload.enqueue(instance.pk)
    )

@receiver(post_save, sender=Photos)
@receiver(post_delete, sender=Photos)
def on_media_change(sender, instance, **kwargs):
    revalidate_frontend_tag("gallery-photos")
