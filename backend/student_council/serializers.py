from rest_framework import serializers
from .models import STUCO, Announcements

class STUCOSeralizer(serializers.ModelSerializer):
    class Meta:
        model = STUCO
        fields = ['council_name', 'group_photo', 'photo_caption', 'stuco_logo']

class AnnouncementSeralizer(serializers.ModelSerializer):
    class Meta:
        model = Announcements
        fields = ['ticker_items']