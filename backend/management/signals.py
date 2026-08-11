from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
 
from .models import PageSettings, SiteSettings
 
def on_post_migrate(sender, app_config, *args, **kwargs):

    if not PageSettings.objects.filter(internal_site_name="AB").exists():
        PageSettings.objects.create(
            internal_site_name="AB",
            title="About STUCO",
            subtitle="",
            tagline="What about it? It's the student council...",
        )

    if not PageSettings.objects.filter(internal_site_name="GL").exists():
        PageSettings.objects.create(
            internal_site_name="GL",
            title="Gallery",
            subtitle="",
            tagline="Capturing the moments that matter most",
        )

    if not PageSettings.objects.filter(internal_site_name="CL").exists():
        PageSettings.objects.create(
            internal_site_name="CL",
            title="Find Your",
            subtitle="Club",
            tagline="A million ways to get involved, one club at a time"
        )

    if not PageSettings.objects.filter(internal_site_name="HM").exists():
        PageSettings.objects.create(
            internal_site_name="HM",
            title="Welcome To",
            subtitle="STUCO",
            tagline="Where students come together",
        )
        
def revalidate_frontend_tag(tag: str) -> None:
    """
    POST to the Next.js revalidation route handler so it drops its
    cached data for the given cacheTag(...) immediately, instead of
    waiting for cacheLife('minutes') to expire naturally.
 
    Fails silently (logged) so a frontend outage never blocks an
    admin save.
    """
    import logging
    import requests
    from django.conf import settings
 
    logger = logging.getLogger(__name__)
 
    url = getattr(settings, "FRONTEND_REVALIDATE_URL", None)
    secret = getattr(settings, "REVALIDATE_SECRET", None)
 
    if not url or not secret:
        logger.warning(
            "Skipping frontend revalidation for tag=%r: "
            "FRONTEND_REVALIDATE_URL / REVALIDATE_SECRET not configured",
            tag,
        )
        return
 
    try:
        response = requests.post(
            url,
            json={"tag": tag},
            headers={"x-revalidate-secret": secret},
            timeout=5,
        )
        response.raise_for_status()
    except requests.RequestException:
        logger.exception("Failed to revalidate frontend tag=%r", tag)
 
 
@receiver(post_save, sender=SiteSettings)
@receiver(post_delete, sender=SiteSettings)
@receiver(post_save, sender=PageSettings)
@receiver(post_delete, sender=PageSettings)
def on_management_change(sender, instance, **kwargs):
    revalidate_frontend_tag("management")