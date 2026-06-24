from .models import Club
from rest_framework import viewsets
from .serializers import ClubSerializer, ClubWhyJoinSerializer

class ClubViewSet(viewsets.ModelViewSet):
    queryset = Club.objects.all()
    serializer_class = ClubSerializer

class ClubWhyJoinViewSet(viewsets.ModelViewSet):
    serializer_class = ClubWhyJoinSerializer

    def perform_create(self, serializer):
        pass # add logic that adds 1 index to all model instances with higher indexes

    def perform_update(self, serializer):
        pass # check if it modifies index, if so, do same as perform_create()

    def perform_destroy(self, instance):
        pass # add logic that subtracts 1 index to all model instances with higher indexes