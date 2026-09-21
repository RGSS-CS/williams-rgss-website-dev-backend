from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('photos', views.PhotoViewset, basename='photos')

urlpatterns = [
    path('', include(router.urls))
]
