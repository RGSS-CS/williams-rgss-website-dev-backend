from rest_framework import viewsets
from .serializers import PageSettingsSerializer, SiteSettingsSerializer, LegalSerializer
from .models import PageSettings, SiteSettings, Legal

class SiteSettingsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = SiteSettings.objects.all()
    serializer_class = SiteSettingsSerializer


class PageSettingsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = PageSettings.objects.all()
    serializer_class = PageSettingsSerializer

class LegalViewset(viewsets.ReadOnlyModelViewSet):
    queryset = Legal.objects.all()
    serializer_class = LegalSerializer