from .models import Club
from rest_framework import viewsets
from .serializers import ClubSerializer, PublicClubSerializer

class ClubViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Club.objects.all()
    serializer_class = ClubSerializer

    def get_serializer_class(self):
        if self.request.user.is_authenticated:
            return ClubSerializer
        return PublicClubSerializer
