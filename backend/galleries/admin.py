from django.contrib import admin
from django.contrib.admin.widgets import AdminFileWidget
from .models import Photos, Videos
from django import forms
from django.core.exceptions import ValidationError

class PhotoAdminForm(forms.ModelForm):
    def clean_upload(self):
        max_size = 2.5 * 1024 * 1024
        if self.size > max_size:
            raise ValidationError(f'The image is too large. Max size is 2.5MB')
    
    image = forms.ImageField(
        validators=[clean_upload],
        widget=AdminFileWidget(attrs={'accept': 'image/*'}),
    )
    
@admin.register(Photos)
class PhotoAdmin(admin.ModelAdmin):
    fields = ('name', 'description', 'image', 'club', 'created_date', 'modified_date')
    readonly_fields = ('created_date','modified_date')
    form = PhotoAdminForm

def validate_video_size(upload):
    if upload.size > 4 * 1024 ** 3:
        raise ValidationError('The video file is too large. The max size is 4 GiB.')


class VideoAdminForm(forms.ModelForm):
    video_file = forms.FileField(
        required=False,
        validators=[validate_video_size],
        widget=AdminFileWidget(),
    )


@admin.register(Videos)
class VideoAdmin(admin.ModelAdmin):
    fields = ('name', 'description','link', 'video_file', 'club', 'created_date', 'modified_date')
    readonly_fields = ('created_date','modified_date')
    form = VideoAdminForm
