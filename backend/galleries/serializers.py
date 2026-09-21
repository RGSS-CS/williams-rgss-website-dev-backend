from rest_framework import serializers
from .models import Photos

class PhotoSeralizer(serializers.ModelSerializer):
    class Meta: 
        model = Photos
        fields = ['name', 'description', 'image', 'created_date',
                  'modified_date', 'club', 'shown_in_gallery', 'shown_in_main_page']
