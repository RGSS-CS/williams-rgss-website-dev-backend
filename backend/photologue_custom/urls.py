from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import ClubGalleryPhotoView, ClubGalleryView, GalleryViewSet, PhotoViewSet

router = DefaultRouter()

router.register("galleries", GalleryViewSet, basename="gallery")
router.register("photos", PhotoViewSet, basename="photo")

urlpatterns = [
    path("clubs/<int:club_id>/gallery/", ClubGalleryView.as_view(), name="club-gallery"),
    path("clubs/<int:club_id>/gallery/photos/", ClubGalleryPhotoView.as_view(), name="club-gallery-photos"),
] + router.urls