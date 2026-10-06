from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Photos, MassImport
from django_tasks import signals
from django.db import transaction
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
    from management.signals import revalidate_frontend_tag

    revalidate_frontend_tag("gallery-photos")
