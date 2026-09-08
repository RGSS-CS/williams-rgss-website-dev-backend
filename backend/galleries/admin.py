from django.contrib import admin
from .models import Photos, Videos

@admin.register(Photos)
class PhotoAdmin(admin.ModelAdmin):
    fields = ('name', 'description', 'image', 'club', 'created_date', 'modified_date')
    readonly_fields = ('created_date','modified_date')

@admin.register(Videos)
class VideoAdmin(admin.ModelAdmin):
    fields = ('name', 'description','link', 'video_file', 'club', 'created_date', 'modified_date')
    readonly_fields = ('created_date','modified_date')
