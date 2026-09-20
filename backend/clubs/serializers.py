from rest_framework import serializers
from taggit.serializers import TagListSerializerField, TaggitSerializer
from .models import Club, ClubAnnouncement

class ClubAnnouncementSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClubAnnouncement
        fields = ["title", "description", "date_posted", "popup",'expiry']

class ClubSerializer(TaggitSerializer, serializers.ModelSerializer):
    category = TagListSerializerField()
    announcement = ClubAnnouncementSerializer(source="club_announcement",many=True,max_length=1)

    class Meta:
        model = Club
        fields = [
            "id", 'visible', "name", "preview_description", "description",
            "tagline", "category", "day_of_meeting", "time",
            "repetition", "location", "classroom_code",
            "accepting_applicants", "join_instructions", "application_form_link",
            "teacher_advisor", "announcement"
            ]

class PublicClubSerializer(TaggitSerializer, serializers.ModelSerializer):
    category = TagListSerializerField()

    class Meta:
        model = Club
        fields = [
            "id", "name", "preview_description", "description",
            "tagline", "category", "day_of_meeting", "time",
            "repetition", "location", "accepting_applicants",
            "teacher_advisor"
            ]
