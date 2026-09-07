from django.db import models
from clubs.models import Club
from pathlib import Path
from uuid import uuid4


def upload_path(instance, filename):
        extension = Path(filename).suffix.lower()
        return f"clubs/{instance.club_id}/photos{uuid4().hex}{extension}"


class Photos(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField(max_length=100,null=True,blank=True, help_text="More like an image caption, to describe what is going on. *OPTIONAL")
    image = models.ImageField(upload_to=upload_path)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)
    club = models.ForeignKey(Club, on_delete=models.CASCADE, null=True)

    class Meta:
        verbose_name_plural = 'Photos'
        verbose_name = 'Photo'



    def __str__(self):
        return self.name
