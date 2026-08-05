from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register("site-settings", views.SiteSettingsViewSet, basename="site-settings")
router.register("page-settings", views.PageSettingsViewSet, basename="page-settings")

urlpatterns = [
    path("", include(router.urls)),
]
