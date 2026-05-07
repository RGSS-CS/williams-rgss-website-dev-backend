from django.urls import path, include, re_path
from . import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register("", views.ClubViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
