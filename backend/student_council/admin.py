from django.contrib import admin
from .models import STUCO, Announcements
from solo.admin import SingletonModelAdmin
from django import forms
from django.contrib.admin import widgets

class STUCOAdminForm(forms.ModelForm):
    class Meta:
        model = STUCO
        fields = [
            'council_name', 'group_photo', 'photo_caption'
        ]
    

@admin.register(STUCO)
class STUCOAdmin(SingletonModelAdmin):
    form = STUCOAdminForm

class AnnouncementsAdminForm(forms.ModelForm):
    class Meta:
        model = Announcements
        fields = [
            'ticker_items'
        ]


@admin.register(Announcements)
class AnnouncementsAdmin(SingletonModelAdmin):
    form = AnnouncementsAdminForm