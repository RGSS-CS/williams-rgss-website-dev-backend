from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework import permissions, status, viewsets
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView
from photologue.models import Gallery, Photo

from clubs.models import Club

from .serializers import (
    GalleryCreateSerializer,
    GallerySerializer,
    PhotoSerializer,
    PhotoUploadSerializer
)


class GalleryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Gallery.objects.all()
    serializer_class = GallerySerializer


class PhotoViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Photo.objects.all()
    serializer_class = PhotoSerializer


class ClubGalleryView(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get(self, request, club_id):
        club = get_object_or_404(Club, pk=club_id)
        if club.gallery is None:
            return Response(
                {"detail": "This club has no gallery yet."},
                status=status.HTTP_404_NOT_FOUND
            )
        return Response(GallerySerializer(club.gallery, context={"request": request}).data)

    def post(self, request, club_id):
        club = get_object_or_404(Club, pk=club_id)
        if club.gallery is not None:
            return Response(
                {"detail": "This club already has a gallery.", "gallery_id": club.gallery_id},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = GalleryCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        with transaction.atomic():
            gallery = serializer.save()
            club.gallery = gallery
            club.save(update_fields=["gallery"])

        return Response(
            GallerySerializer(gallery, context={"request": request}).data,
            status=status.HTTP_201_CREATED
        )


class ClubGalleryPhotoView(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    parser_classes = [MultiPartParser, FormParser]

    def _get_gallery(self, club_id):
        club = get_object_or_404(Club, pk=club_id)
        if club.gallery is None:
            return None
        return club.gallery

    def get(self, request, club_id):
        gallery = self._get_gallery(club_id)
        if gallery is None:
            return Response(
                {"detail": "This club has no gallery yet."},
                status=status.HTTP_404_NOT_FOUND
            )
        return Response(PhotoSerializer(gallery.photos.all(), many=True, context={"request": request}).data)

    def post(self, request, club_id):
        gallery = self._get_gallery(club_id)
        if gallery is None:
            return Response(
                {"detail": "This club has no gallery yet. Create one first via POST /api/photologue/clubs/<club_id>/gallery/."},
                status=status.HTTP_404_NOT_FOUND
            )

        files = request.FILES.getlist("images") or (
            [request.FILES["image"]] if "image" in request.FILES else []
        )
        if not files:
            return Response(
                {"detail": "No image(s) provided. Send under 'image' (single) or 'images' (multiple)."},
                status=status.HTTP_400_BAD_REQUEST
            )

        caption = request.data.get("caption", "")
        is_public = request.data.get("is_public", True)

        created = []
        errors = []
        with transaction.atomic():
            for f in files:
                serializer = PhotoUploadSerializer(
                    data={"image": f, "caption": caption, "is_public": is_public}
                )
                if not serializer.is_valid():
                    errors.append({"file": f.name, "errors": serializer.errors})
                    continue
                photo = serializer.save()
                gallery.photos.add(photo)
                created.append(PhotoSerializer(photo, context={"request": request}).data)

            if errors and not created:
                # Nothing succeeded — roll back and report why.
                transaction.set_rollback(True)
                return Response({"errors": errors}, status=status.HTTP_400_BAD_REQUEST)

        response_body = {"created": created}
        if errors:
            response_body["errors"] = errors
        return Response(response_body, status=status.HTTP_201_CREATED)
