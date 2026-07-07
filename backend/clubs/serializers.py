from rest_framework import serializers
from taggit.serializers import TagListSerializerField, TaggitSerializer
from .models import Club, ClubGalleryImage

class ClubGalleryImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClubGalleryImage
        fields = ["id", "club_id", "image", "name", "description", "category"]

class ClubSerializer(TaggitSerializer, serializers.ModelSerializer):
    category = TagListSerializerField()
    
    class Meta:
        model = Club
        fields = [
            "id", "name", "preview_description", "description", "tagline", "category",
            "day_of_meeting", "time", "repetition", "room_num",
            "classroom_code", "accepting_applicants", "application_form_link", "teacher_advisor",
            ]

# TODO: add serializer for club SM sites
