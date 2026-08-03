from rest_framework import serializers
from .models import SiteSettings, SocialMedia, Location, PageSettings
from phonenumber_field.serializerfields import PhoneNumberField #type: ignore

class PhoneNumberSerializer(serializers.Serializer):
    school_phone = PhoneNumberField(region="CA")

class SocialMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = SocialMedia
        fields = ["site", "content_type", "object_id"]

class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ["location", "location_lat", "location_lon", "content_type", "object_id"]

class SiteSettingsSerializer(serializers.ModelSerializer):
    social_media = SocialMediaSerializer(many=True, read_only=True)
    school_location = LocationSerializer(many=True, read_only=True)

    class Meta:
        model = SiteSettings
        fields = ["maintainance_mode", 
                  "school_name",
                  "council_name", 
                  "school_email",
                  "school_phone",
                  "social_media", 
                  "favicon", 
                  "stuco_image", 
                  "about_stuco", 
                  "about_school", 
                  "school_location",
                  "school_mascot", 
                  "school_primary_color", 
                  "school_secondary_color", 
                  "school_tertiary_color"]

class PageSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = PageSettings
        fields = [
            "internal_site_name",
            "title",
            "subtitle",
            "tagline"
        ]