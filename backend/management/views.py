from rest_framework import viewsets
from .serializers import PageSettingsSerializer, SiteSettingsSerializer
from .models import PageSettings, SiteSettings

class SiteSettingsViewSet(viewsets.ModelViewSet):
    queryset = SiteSettings.objects.all()
    serializer_class = SiteSettingsSerializer

class PageSettingsViewSet(viewsets.ModelViewSet):
    queryset = PageSettings.objects.all()
    serializer_class = PageSettingsSerializer