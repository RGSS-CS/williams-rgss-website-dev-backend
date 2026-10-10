from rest_framework import viewsets
from .serializers import STUCOSeralizer, AnnouncementSeralizer
from .models import Stuco, Announcements 

class STUCOViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Stuco.objects.all()
    serializer_class = STUCOSeralizer

class AnnouncementViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Announcements.objects.all()
    serializer_class = AnnouncementSeralizer