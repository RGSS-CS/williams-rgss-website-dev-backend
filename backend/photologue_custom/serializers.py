from rest_framework import serializers
from photologue.models import Gallery, Photo


class PhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Photo
        fields = [
            "id",
            "title",
            "image",
            "caption",
            "date_added",
        ]


class GallerySerializer(serializers.ModelSerializer):
    photos = PhotoSerializer(many=True, read_only=True)

    class Meta:
        model = Gallery
        fields = [
            "id",
            "title",
            "description",
            "date_added",
            "photos",
        ]