from django.core.management.base import BaseCommand

from management.signals import revalidate_frontend_tag


class Command(BaseCommand):
    help = "Revalidate all frontend cache tags once during application startup."

    def handle(self, *args, **options):
        for tag in (
            "management",
            "legal",
            "clubs",
            "gallery-photos",
            "stuco-settings",
        ):
            revalidate_frontend_tag(tag)
