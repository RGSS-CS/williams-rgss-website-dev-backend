from rest_framework import viewsets
from .serializers import PageSettingsSerializer, SiteSettingsSerializer
from .models import PageSettings, SiteSettings
from rest_framework.permissions import IsAdminUser

class SiteSettingsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = SiteSettings.objects.all()
    serializer_class = SiteSettingsSerializer


class PageSettingsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = PageSettings.objects.all()
    serializer_class = PageSettingsSerializer