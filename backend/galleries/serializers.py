from rest_framework import serializers
from .models import Photos

class PhotoSeralizer(serializers.ModelSerializer):
    category = serializers.SerializerMethodField()

    def get_category(self, obj):
        if obj.club is None:
            return []
        return list(obj.club.category.names())

    class Meta: 
        model = Photos
        fields = ['name', 'description', 'image', 'created_date',
                  'modified_date', 'club', 'category', 'shown_in_gallery', 'shown_in_main_page']
