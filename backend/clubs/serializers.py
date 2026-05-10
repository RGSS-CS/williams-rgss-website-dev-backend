from rest_framework import serializers
from .models import Club #, ClubGalleryImage

class ClubSerializer(serializers.ModelSerializer):
    class Meta:
        model = Club
        fields = ["id", "name", "description", "calendar"]
        