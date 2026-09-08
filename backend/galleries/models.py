from django.db import models
from clubs.models import Club
from pathlib import Path
from uuid import uuid4


def photo_upload_path(instance, filename):
        extension = Path(filename).suffix.lower()
        return f"clubs/{instance.club_id}/photos/{uuid4().hex}{extension}"

def video_upload_path(instance, filename):
        extension = Path(filename).suffix.lower()
        return f"clubs/{instance.club_id}/videos/{uuid4().hex}{extension}"


class Photos(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField(max_length=100,null=True,blank=True, help_text="More like an image caption, to describe what is going on. *OPTIONAL")
    image = models.ImageField(upload_to=photo_upload_path)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)
    club = models.ForeignKey(Club, on_delete=models.CASCADE, null=True)

    class Meta:
        verbose_name_plural = 'Photos'
        verbose_name = 'Photos'

    def __str__(self):
        return self.name
    
class Videos(models.Model):
    class VideoType(models.TextChoices):
         YOUTUBE = "YT", "Youtube"
         GOOGLE_DRIVE = 'GD', 'Google Drive'
         OTHER = 'OT', 'Other'

    name = models.CharField(max_length=50)
    link = models.URLField(max_length=500, blank=True, null=True, help_text='Not required, only needed for Youtube and Google Drive(Use embed code)')
    video_file = models.FileField(upload_to=video_upload_path)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)
    club = models.ForeignKey(Club, on_delete=models.CASCADE, null=True)

    class Meta: 
        verbose_name = 'Videos'
        verbose_name_plural = 'Videos'

    def __str__(self):
         return self.name