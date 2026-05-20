from rest_framework import serializers
from .models import Club, ClubGalleryImage

class ClubGalleryImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClubGalleryImage
        fields = ["id", "club_id", "image", "name", "description", "category"]

class ClubSerializer(serializers.ModelSerializer):
    # Causeing: AssertionError at /club/
    # galleryImages = ClubGalleryImageSerializer(many=True, read_only=True)

    class Meta:
        model = Club
        fields = ["id", "name", "description", "motto", "calendar", "classroom_code"]
        extra_kwargs = {
            "galleryImages": {"required": False, "allow_blank": True}
        }
        
# TODO: add serializer for club SM sites
