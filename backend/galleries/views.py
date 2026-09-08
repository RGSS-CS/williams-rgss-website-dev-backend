from rest_framework import viewsets
from .serializers import VideoSerializer, PhotoSeralizer
from .models import Videos, Photos
from rest_framework.permissions import IsAdminUser, AllowAny

class VideoViewset(viewsets.ModelViewSet):
    queryset = Videos.objects.all()
    serializer_class = VideoSerializer

    def get_permissions(self):
        self.permission_classes = [AllowAny]
        if self.request.method == 'POST':
            self.permission_classes = [IsAdminUser]

        return super().get_permissions()
    
class PhotoViewset(viewsets.ModelViewSet):
    queryset = Videos.objects.all()
    serializer_class = PhotoSeralizer

    def get_permissions(self):
        self.permission_classes = [AllowAny]
        if self.request.method == 'POST':
            self.permission_classes = [IsAdminUser]

        return super().get_permissions()
