from rest_framework import serializers
from taggit.serializers import TagListSerializerField, TaggitSerializer
from .models import Club, ClubWhyJoin
from photologue_custom.serializers import GallerySerializer

class ClubWhyJoinSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClubWhyJoin
        fields = ["title", "description", "index"]

class ClubSerializer(TaggitSerializer, serializers.ModelSerializer):
    category = TagListSerializerField()
    why_join = ClubWhyJoinSerializer(many=True, read_only=True)
    gallery = GallerySerializer(read_only = True)

    class Meta:
        model = Club
        fields = [
            "id", 
            "name", 
            "preview_description", 
            "description", 
            "tagline", 
            "category",
            "day_of_meeting",
            "time", 
            "repetition", 
            "room_number", 
            "why_join",
            "classroom_code", 
            "accepting_applicants", 
            "join_instructions", 
            "application_form_link", 
            "teacher_advisor",
            "gallery"
            ]

class PublicClubSerializer(TaggitSerializer, serializers.ModelSerializer):
    category = TagListSerializerField()
    why_join = ClubWhyJoinSerializer(many=True, read_only=True)

    class Meta:
        model = Club
        fields = [
            "id", 
            "name", 
            "preview_description", 
            "description", 
            "tagline", 
            "category",
            "day_of_meeting",
            "time", 
            "repetition", 
            "room_number", 
            "why_join",
            "teacher_advisor",
            ]

# TODO: add serializer for club SM sites