from django.urls import path, include, re_path
from . import views

urlpatterns = [
    path("get/<int:pk>/info/", views.club_info, name="clubs_club_info"),
]
