from rest_framework import serializers
from .models import Club, ClubGalleryImage

class ClubGalleryImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClubGalleryImage
        fields = ["id", "club_id", "image", "name", "description"]

class ClubSerializer(serializers.ModelSerializer):
    galleryImages = ClubGalleryImageSerializer(many=True, read_only=True)

    class Meta:
        model = Club
        fields = ["id", "name", "description", "motto", "calendar", "galleryImages", "classroom_code"]
        
# TODO: add serializer for club SM sites
