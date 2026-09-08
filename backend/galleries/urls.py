from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('videos', views.VideoSerializer, basename='videos')
router.register('photos', views.PhotoSeralizer, basename='photos')

urlpatterns = [
    path('', include(router.urls))
]