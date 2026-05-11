from rest_framework import serializers
from .models import Club, ClubGalleryImage

class ClubGalleryImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClubGalleryImage
        fields = ["club.pk", "image", "name", "description"]

class ClubSerializer(serializers.ModelSerializer):
    galleryImage = ClubGalleryImageSerializer(many=True, read_only=True)

    class Meta:
        model = Club
        fields = ["id", "name", "description", "calendar", "galleryImage"]
        