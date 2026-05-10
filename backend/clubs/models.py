from django.db import models
from django.utils import timezone
from taggit.managers import TaggableManager
from PIL import Image

class Club(models.Model):
    #group = models.OneToOneField(Group, on_delete=models.CASCADE, related_name='group')
    name = models.CharField(max_length=100)
    description = models.TextField(default="", max_length=500)
    tags = TaggableManager()
    image = models.ImageField(default="default.jpg", upload_to="clubs/images")
    # TODO: add other neeeded fields

    # club name
    # club motto
    # club location
    # club schedule
    # club profile picture
    # club main category
    # club tags
    # club social media URLs
    # club description
    # club gallery/images bank
    # club execs list
    # a. club exec profile picture
    # b. club exec position

    def __str__(self):
        return self.name
    
    def save(self):
        super().save()
        
        img = Image.open(self.image.path)
        
        if img.height > 300 or img.width > 300:
            output_size = (300, 300)
            img.thumbnail(output_size)
            img.save(self.image.path)

def get_upload_path(instance, filename):
    return f"clubs/gallery/{instance.club.pk}/{filename}"

class ClubGalleryImage(models.Model):
    club = models.ForeignKey(Club, related_name='galleryImage', on_delete=models.CASCADE)
    image = models.ImageField(default="default.jpg", upload_to=get_upload_path)
    name = models.CharField(max_length=100)
    description = models.TextField(default="", max_length=500)

    def save(self):
        super().save()
        
        img = Image.open(self.image.path)
        
        if img.height > 300 or img.width > 300:
            output_size = (300, 300)
            img.thumbnail(output_size)
            img.save(self.image.path)
