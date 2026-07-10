from django.shortcuts import get_object_or_404, redirect
from management.models import SiteSettings

def redirect_frontend(request):
    settings = SiteSettings.get_solo()
    return redirect(settings.frontend_url)