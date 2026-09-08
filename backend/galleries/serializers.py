from rest_framework import serializers
from .models import Videos, Photos

class VideoSerializer(serializers.ModelSerializer):
    class Meta: 
        model = Videos
        fields = ['name', 'description', 'link', 'video_file',
                  'created_date', 'modified_date', 'club', 
                  'shown_in_gallery', 'shown_in_main_page']

class PhotoSeralizer(serializers.ModelSerializer):
    class Meta: 
        model = Photos
        fields = ['name', 'description', 'image', 'created_date',
                  'modified_date', 'club', 'shown_in_gallery', 'shown_in_main_page']

