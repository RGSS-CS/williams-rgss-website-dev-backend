from .models import PageSettings

def on_post_migrate(sender, app_config, *args, **kwargs):
    if not PageSettings.objects.filter(internal_site_name="HM").exists():
        PageSettings.objects.create(
            internal_site_name="HM",
            title="School Home",
            subtitle="",
            tagline="",
        )
    if not PageSettings.objects.filter(internal_site_name="CL").exists():
        PageSettings.objects.create(
            internal_site_name="CL",
            title="Clubs",
            subtitle="",
            tagline="",
        )
    if not PageSettings.objects.filter(internal_site_name="GL").exists():
        PageSettings.objects.create(
            internal_site_name="GL",
            title="Gallery",
            subtitle="",
            tagline="",
        )
    if not PageSettings.objects.filter(internal_site_name="AB").exists():
        PageSettings.objects.create(
            internal_site_name="AB",
            title="About School",
            subtitle="",
            tagline="",
        )