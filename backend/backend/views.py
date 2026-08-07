from django.http import HttpResponse
from django.shortcuts import redirect
from management.models import SiteSettings

def redirect_frontend(request):
    settings = SiteSettings.get_solo()

    if not settings.frontend_url:
        return HttpResponse("Frontend URL has not been configured.", status=500)

    return redirect(settings.frontend_url)
