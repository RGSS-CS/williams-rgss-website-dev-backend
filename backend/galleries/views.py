from rest_framework import viewsets
from .serializers import VideoSerializer, PhotoSeralizer
from .models import Videos, Photos
from rest_framework.permissions import IsAdminUser, AllowAny

class VideoViewset(viewsets.ReadOnlyModelViewSet):
    queryset = Videos.objects.all()
    serializer_class = VideoSerializer
    
class PhotoViewset(viewsets.ReadOnlyModelViewSet):
    queryset = Photos.objects.all()
    serializer_class = PhotoSeralizer