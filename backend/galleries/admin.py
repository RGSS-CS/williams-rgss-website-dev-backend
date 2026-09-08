from django.contrib import admin
from .models import Photos, Videos

@admin.register(Photos)
class PhotoAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'image', 'club', 'created_date', 'modified_date')
    fields = list_display
    readonly_fields = ('created_date','modified_date','name')


@admin.register(Videos)
class VideoAdmin(admin.ModelAdmin):
    list_display = ('name', 'description','link', 'video_file', 'club', 'created_date', 'modified_date')
    fields = list_display
    readonly_fields = ('created_date','modified_date','name')
