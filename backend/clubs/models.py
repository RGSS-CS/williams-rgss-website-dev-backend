from django.db import models
from django.utils import timezone
from django.contrib.auth.models import Group
from taggit.managers import TaggableManager
from PIL import Image

class Club(models.Model):
    #group = models.OneToOneField(Group, on_delete=models.CASCADE, related_name='group')
    name = models.CharField(max_length=100)
    description = models.TextField(default="", max_length=500)
    tags = TaggableManager()
    image = models.ImageField(default="default.jpg", upload_to="clubs/images")
    # TODO: add other neeeded fields

    def __str__(self):
        return self.name
    
    def save(self):
        super().save()
        
        img = Image.open(self.image.path)
        
        if img.height > 300 or img.width > 300:
            output_size = (300, 300)
            img.thumbnail(output_size)
            img.save(self.image.path)

class ClubGalleryImage(models.Model):
    club = models.ForeignKey(Club, related_name='galleryImage', on_delete=models.CASCADE)
    image = models.ImageField(default="default.jpg", upload_to=f"clubs/gallery/{club.pk}/")
    name = models.CharField(max_length=100)
    description = models.TextField(default="", max_length=500)

    def save(self):
        super().save()
        
        img = Image.open(self.image.path)
        
        if img.height > 300 or img.width > 300:
            output_size = (300, 300)
            img.thumbnail(output_size)
            img.save(self.image.path)
