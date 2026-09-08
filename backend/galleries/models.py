from django.db import models
from clubs.models import Club
from pathlib import Path
from uuid import uuid4
from django.utils.crypto import get_random_string
from django.core.exceptions import ValidationError


def photo_upload_path(instance, filename):
        extension = Path(filename).suffix.lower()
        return f"clubs/{instance.club_id}/photos/{uuid4().hex}{extension}"

def video_upload_path(instance, filename):
        extension = Path(filename).suffix.lower()
        return f"clubs/{instance.club_id}/videos/{uuid4().hex}{extension}"

def zip_upload_path(instance, filename):
     extension = Path(filename).suffix.lower()
     return f"clubs/{instance.club_id}/temp/zip/{uuid4().hex}{extension}"

class MassImport(models.Model):
    class FileType(models.TextChoices):
         PHOTOS = 'PH', 'Photos'
         VIDEOS = 'VI', 'Videos'
    name = models.CharField(null=True, blank=True, help_text='The name will automatically be generated based on the ZIP file name.')
    club = models.ForeignKey(Club, on_delete=models.CASCADE, null=True)
    zip_file = models.FileField(upload_to=zip_upload_path, help_text='EVERYTHING within the ZIP file will be uploaded into the specified club. Videos or Photo files only.')
    file_type = models.CharField(max_length=2, choices=FileType)
    upload_date = models.DateTimeField(auto_now_add=True)
    upload_status = models.CharField(max_length=5, null=True)

    class Meta:
        verbose_name = 'ZIP Upload'
        verbose_name_plural = 'ZIP Upload'

    def __str__(self):
         return self.name

    def save(self, *args, **kwargs):
         club_name = self.club.name
         file = self.zip_file.name
         self.name = f'{file} - {club_name[:17]}'
         super().save(*args, **kwargs)

class Photos(models.Model):
    name = models.CharField(max_length=50, null=True, blank=True, help_text='If left blank, it will automatically generate a name for you.')
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

    def save(self, *args, **kwargs):
        if not self.name or not self.name.strip:
            club_name = self.club.name
            self.name = f'{club_name[:17]} - {get_random_string(8)}'
            super().save(*args, **kwargs)


class Videos(models.Model):
    class VideoType(models.TextChoices):
         YOUTUBE = "YT", "Youtube"
         GOOGLE_DRIVE = 'GD', 'Google Drive'
         OTHER = 'OT', 'Other'

    name = models.CharField(max_length=50,null=True, blank=True, help_text='If left blank, it will automatically generate a name for you.')
    description = models.TextField(max_length=100, null=True, blank=True, help_text="This is like a video description about what the video is about. *OPTIONAL.")
    link = models.URLField(max_length=500, blank=True, null=True, help_text='Not required, only needed for Youtube and Google Drive(Use embed code)')
    video_file = models.FileField(upload_to=video_upload_path, null=True, blank=True)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)
    club = models.ForeignKey(Club, on_delete=models.CASCADE, null=True)

    class Meta: 
        verbose_name = 'Videos'
        verbose_name_plural = 'Videos'

    def __str__(self):
         return self.name

    def save(self, *args, **kwargs):
        if not self.name or not self.name.strip:
            club_name = self.club.name
            self.name = f'{club_name[:17]} - {get_random_string(8)}'
            super().save(*args, **kwargs)