from django.db import models
from solo.models import SingletonModel
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from PIL import Image
from osm_field.fields import OSMField, LatitudeField, LongitudeField

class SocialMedia(models.Model):
    class Sites(models.TextChoices):
        INSTAGRAM = "IG", "Instagram"
        GITHUB = "GH", "GitHub"
        YOUTUBE = "YT", "YouTube"
        TIKTOK = "TT", "TikTok"
        DISCORD = "DC", "Discord"
        THREADS = "TR", "Threads"
        FACEBOOK = "FB", "Facebook" # doubt anyone uses this, it's old af
        TWITTER = "X", "Twitter/X" # i hate this name
        LINKEDIN = "LI", "LinkedIn" 
        WEBSITE = "WS", "Website"
        OTHER = "OT", "Other"
        # not adding reddit for obvious reasons

    # club = models.ForeignKey(Club, related_name='socialMedia', on_delete=models.CASCADE)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveBigIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")
    site = models.CharField(max_length=2, choices=Sites.choices, default=Sites.OTHER)

    def __str__(self):
        return self.site
    
    class Meta:
        indexes = [
            models.Index(fields=["content_type", "object_id"])
        ]

class Location(models.Model):
    location = OSMField()
    location_lat = LatitudeField()
    location_lon = LongitudeField()

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveBigIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")

class SiteSettings(SingletonModel):
    maintainance_mode = models.BooleanField(default=False)
    site_name = models.CharField(default="SCHOOL STUCO", max_length=50)
    social_media = GenericRelation(SocialMedia)
    favicon = models.ImageField(default="management/default.png", upload_to="management/")
    stuco_image = models.ImageField(default="management/default.png", upload_to="management/")
    about_stuco = models.TextField(blank=True, max_length=500)
    about_school = models.TextField(blank=True, max_length=500)
    # TODO: add website maintainers once users are done
    school_location = GenericRelation(Location)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        
        img = Image.open(self.stuco_image.path)
        
        if img.height > 300 or img.width > 300:
            output_size = (300, 300)
            img.thumbnail(output_size)
            img.save(self.stuco_image.path)

    def __str__(self):
        return "Site Configuration"

    class Meta:
        verbose_name = "Site Configuration"
