from rest_framework import serializers
from .models import SiteSettings, SocialMedia, Location

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
                  "site_name", 
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
