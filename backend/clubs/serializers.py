from rest_framework import serializers
from taggit.serializers import TagListSerializerField, TaggitSerializer
from photologue_custom.serializers import ClubGalleryPhotoSerializer
from .models import Club, ClubWhyJoin

class ClubWhyJoinSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClubWhyJoin
        fields = ["title", "description", "index"]

class ClubSerializer(TaggitSerializer, serializers.ModelSerializer):
    category = TagListSerializerField()
    why_join = ClubWhyJoinSerializer(many=True, read_only=True)
    gallery_photos = serializers.SerializerMethodField()

    def get_gallery_photos(self, obj):
        if not obj.gallery:
            return []
        return ClubGalleryPhotoSerializer(
            obj.gallery.photos.all(), many=True, context=self.context
        ).data

    class Meta:
        model = Club
        fields = [
            "id", "name", "preview_description", "description", "tagline", "category",
            "day_of_meeting", "time", "repetition", "room_number", "why_join",
            "classroom_code", "accepting_applicants", "join_instructions", "application_form_link", "teacher_advisor",
            "gallery_photos", "thumbnail"
            ]

# TODO: add serializer for club SM sites