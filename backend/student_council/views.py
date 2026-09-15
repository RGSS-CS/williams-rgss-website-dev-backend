from rest_framework import viewsets
from .serializers import STUCOSeralizer, AnnouncementSeralizer
from .models import STUCO, Announcements 

class STUCOViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = STUCO.objects.all()
    serializer_class = STUCOSeralizer

class AnnouncementViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Announcements.objects.all()
    serializer_class = AnnouncementSeralizer