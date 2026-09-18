from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('stuco-settings', views.STUCOViewSet, basename='stuco-settings')
router.register('announcements', views.AnnouncementViewSet, basename='announcements')

urlpatterns = [
    path('', include(router.urls))
]