from rest_framework import serializers
from taggit.serializers import TagListSerializerField, TaggitSerializer
from .models import Club, ClubWhyJoin, ClubMembership, ClubChanges
from photologue_custom.serializers import GallerySerializer

class ClubWhyJoinSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClubWhyJoin
        fields = ["title", "description", "index"]

class ClubSerializer(TaggitSerializer, serializers.ModelSerializer):
    category = TagListSerializerField()
    why_join = ClubWhyJoinSerializer(source="why_join_reasons",many=True, read_only=True)
    gallery = GallerySerializer(read_only = True)

    class Meta:
        model = Club
        fields = [
            "id", "name", "preview_description", "description", 
            "tagline", "category", "day_of_meeting", "time", 
            "repetition", "room_number", "why_join", "classroom_code", 
            "accepting_applicants", "join_instructions", "application_form_link", 
            "teacher_advisor", "gallery"
            ]

class PublicClubSerializer(TaggitSerializer, serializers.ModelSerializer):
    category = TagListSerializerField()
    why_join = ClubWhyJoinSerializer(source="why_join_reasons", many=True, read_only=True)

    class Meta:
        model = Club
        fields = [
            "id", "name", "preview_description", "description", 
            "tagline", "category", "day_of_meeting", "time", 
            "repetition", "room_number", "why_join", "accepting_applicants",
            "teacher_advisor",
            ]

class ClubMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClubMembership
        fields = [
            "id", "user", "club", "role",
            "bypass_confirmation_restrictions",
            "created", "updated"
        ]
        read_only_fields = ["created", "updated"]

class ClubChangesSerializer(serializers.ModelSerializer):
    submitted_by = serializers.PrimaryKeyRelatedField(read_only = True)
    reviewed_by = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = ClubChanges
        fields = [
            "id", "club", "changes", "status",
            "submitted_by", "submitted_at",
            "reviewed_by", "reviewed_at", "review_note",
        ]
        read_only_fields = [
            "status", "submitted_by", "submitted_at",
            "reviewed_by", "reviewed_at", "review_note",
        ]
    def validate_change(self, change):
        unknown = set(change) - set(Club.PENDING_APPROVAL_FIELDS)
        if unknown:
            raise serializers.ValidationError(f"These fields cannot be submitted for approval: {','.join(sorted(unknown))}")
        return change

class ClubChangesReviewSeralizer(serializers.Serializer):
    note = serializers.CharField(required= False, allow_blank= True, default="")
    
# TODO: add serializer for club SM sites