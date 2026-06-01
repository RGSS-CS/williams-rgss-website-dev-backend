from rest_framework import serializers
from .models import SiteSettings

class SiteSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = SiteSettings
        fields = ["maintainance_mode", "site_name", "social_media", 
                  "favicon", "stuco_image", "about_stuco", 
                  "about_school", "school_location"]
