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

@admin.register(Videos)
class VideoAdmin(admin.ModelAdmin):
    fields = ('name', 'description','link', 'video_file', 'club', 'created_date', 'modified_date')
    readonly_fields = ('created_date','modified_date')
