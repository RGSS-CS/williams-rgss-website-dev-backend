import uuid

from django.utils.text import slugify
from rest_framework import serializers
from photologue.models import Gallery, Photo


class PhotoSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    def get_image(self, obj):
        if not obj.image:
            return None

        request = self.context.get("request")
        if not request:
            return obj.image.url

        return request.build_absolute_uri(obj.image.url).replace("http://", "https://", 1)

    class Meta:
        model = Photo
        fields = [
            "id",
            "title",
            "image",
            "caption",
            "date_added"
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
            "photos"
        ]


def _unique_slug(model, base):
    """
    photologue's Gallery/Photo slugs are unique site-wide (see the `unique=True`
    constraint on both models' `slug` fields in photologue/models.py), so a
    plain slugify(title) collides as soon as two clubs pick similar names.
    Appending a short uuid4 fragment keeps it unique without user input.
    """
    base = slugify(base) or "item"
    return f"{base}-{uuid.uuid4().hex[:8]}"


class GalleryCreateSerializer(serializers.ModelSerializer):
    """
    Creates a new photologue Gallery. `slug` is derived from `title` since
    Gallery has no auto-slugify save() override (unlike Photo) — confirmed by
    reading photologue/models.py, where Gallery.save() is not overridden at all.
    """

    class Meta:
        model = Gallery
        fields = ["id", "title", "description", "is_public"]
        read_only_fields = ["id"]

    def create(self, validated_data):
        validated_data["slug"] = _unique_slug(Gallery, validated_data["title"])
        return super().create(validated_data)


class PhotoUploadSerializer(serializers.ModelSerializer):
    """
    Uploads a single image into a gallery. `title` is optional — if omitted we
    fall back to the uploaded filename, matching how photologue's own
    GalleryUpload admin action behaves.
    """

    title = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = Photo
        fields = ["id", "title", "image", "caption", "is_public"]
        read_only_fields = ["id"]

    def create(self, validated_data):
        title = validated_data.get("title") or validated_data["image"].name
        validated_data["title"] = title
        validated_data["slug"] = _unique_slug(Photo, title)
        return super().create(validated_data)
