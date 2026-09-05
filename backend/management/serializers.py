from rest_framework import serializers
from .models import SiteSettings, SchoolSocialMedia, Location, PageSettings
from image_cropping.utils import get_backend
from phonenumber_field.serializerfields import PhoneNumberField #type: ignore

class PhoneNumberSerializer(serializers.Serializer):
    school_phone = PhoneNumberField(region="CA")

class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ["location", "location_lat", "location_lon", "content_type", "object_id"]

class SocialMediaSeralizer(serializers.ModelSerializer):
    class Meta: 
        model = SchoolSocialMedia
        fields = ['social_type', 'title', 'link']

class SiteSettingsSerializer(serializers.ModelSerializer):
    social_media = SocialMediaSeralizer(many=True, read_only=True)
    school_location = LocationSerializer(many=True, read_only=True)

    cropped_favicon = serializers.SerializerMethodField()
    cropped_site_image = serializers.SerializerMethodField()
 
    def get_cropped_favicon(self, obj):
        if not obj.favicon:
            return None 
        request = self.context.get("request")
        url = get_backend().get_thumbnail_url(
            obj.favicon,
            {
                "size": (32, 32),
                "box": obj.favicon_cropping,
                "crop": True,
                "detail": True
            }
        )
        return url

    def get_cropped_site_image(self, obj):
        if not obj.site_logo:
            return None
        request = self.context.get("request")
        url = get_backend().get_thumbnail_url(
            obj.site_logo,
            {
                "size": (80, 80),
                "box": obj.site_logo_cropping,
                "crop": True,
                "detail": True
            }
        )
        return url
    
    class Meta:
        model = SiteSettings
        fields = [
            "maintainance_mode", 
            "school_name",
            "council_name", 
            "school_email",
            "school_phone",
            "social_media", 
            "cropped_favicon", 
            "cropped_site_image", 
            "school_location",
            "school_mascot", 
            "school_primary_color", 
            "school_secondary_color", 
            "school_tertiary_color",
            "captcha",
            "school_domain"
        ]

class PageSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = PageSettings
        fields = [
            "internal_site_name",
            "title",
            "subtitle",
            "tagline"
        ]
