from rest_framework import viewsets
from .serializers import PhotoSeralizer
from .models import Photos
from rest_framework.permissions import IsAdminUser, AllowAny

class PhotoViewset(viewsets.ReadOnlyModelViewSet):
    queryset = Photos.objects.all()
    serializer_class = PhotoSeralizer
