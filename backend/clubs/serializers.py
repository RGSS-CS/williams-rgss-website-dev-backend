from rest_framework import serializers
from .models import Club, ClubGalleryImage

class ClubSerializer(serializers.ModelSerializer):
    class Meta:
        model = Club
        fields = ["pk", "name", "description", "calendar"]
        