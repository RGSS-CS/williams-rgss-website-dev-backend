from rest_framework import serializers
from photologue.models import Photo


class ClubGalleryPhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Photo
        fields = ["id", "title", "image", "caption", "date_added"]