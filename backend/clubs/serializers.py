from rest_framework import serializers
from taggit.serializers import TagListSerializerField, TaggitSerializer
from .models import Club, ClubGalleryImage

class ClubGalleryImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClubGalleryImage
        fields = ["id", "club_id", "image", "name", "description", "category"]

class ClubSerializer(TaggitSerializer, serializers.ModelSerializer):
    # Causeing: AssertionError at /club/
    # galleryImages = ClubGalleryImageSerializer(many=True, read_only=True)
    category = TagListSerializerField()
    class Meta:
        model = Club
        fields = [
            "id", "name", "description",
            "category", "day_of_meeting", "time",
            "room_num", "classroom_code", "teacher_advisor"
            ]

    def validateCategory(self, value):
        invalid = set(value) - CLUB_CATEGORY_CHOICES
        if invalid:
            raise serializers.ValidationError(
                f"Invalid category: {invalid}."
                f"Valid categories are: {CLUB_CATEGORY_CHOICES}."
            )
        
# TODO: add serializer for club SM sites
