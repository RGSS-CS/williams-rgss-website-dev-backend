from django.contrib.admin.widgets import AdminFileWidget
from .models import STUCO, Announcements
from solo.admin import SingletonModelAdmin
from django import forms
from django.contrib import admin
from galleries.validators import validate_image_upload


class STUCOAdminForm(forms.ModelForm):
    stuco_logo = forms.ImageField(required=False, widget=AdminFileWidget())

    def clean_stuco_logo(self):
        return validate_image_upload(self.cleaned_data['stuco_logo'])

    def clean_group_photo(self):
        return validate_image_upload(self.cleaned_data['group_photo'])

    class Meta:
        model = STUCO
        fields = [
            'council_name', 'group_photo', 'photo_caption','stuco_logo'
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
