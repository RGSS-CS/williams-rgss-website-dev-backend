from django.db import models
from solo.models import SingletonModel
from clubs.models import SocialMedia
from django.contrib.contenttypes.fields import GenericRelation
from PIL import Image
from address.models import AddressField

class SiteSettings(SingletonModel):
    maintainance_mode = models.BooleanField(default=False)
    site_name = models.CharField(default="RGSS STUCO", max_length=50)
    social_media = GenericRelation(SocialMedia)
    favicon = models.ImageField(default="management/default.png", upload_to="management/")
    stuco_image = models.ImageField(default="management/default.png", upload_to="management/")
    about_stuco = models.TextField(blank=True, max_length=500)
    about_school = models.TextField(blank=True, max_length=500)
    # TODO: add website maintainers once users are done
    school_location = AddressField(blank=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        
        img = Image.open(self.image.path)
        
        if img.height > 300 or img.width > 300:
            output_size = (300, 300)
            img.thumbnail(output_size)
            img.save(self.image.path)

    def __str__(self):
        return "Site Configuration"

    class Meta:
        verbose_name = "Site Configuration"
