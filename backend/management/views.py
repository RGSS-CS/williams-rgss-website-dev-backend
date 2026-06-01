from rest_framework import viewsets
from .serializers import SiteSettingsSerializer
from .models import SiteSettings

class ClubViewSet(viewsets.ModelViewSet):
    queryset = SiteSettings.objects.all()
    serializer_class = SiteSettingsSerializer
