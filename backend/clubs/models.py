from django.db import models
from django.utils import timezone
from taggit.managers import TaggableManager
from PIL import Image

class Club(models.Model):
    #group = models.OneToOneField(Group, on_delete=models.CASCADE, related_name='group')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, max_length=500)
    motto = models.TextField(blank=True, max_length=100)
    tags = TaggableManager()
    image = models.ImageField(default="default.jpg", upload_to="clubs/images")
    classroom_code = models.CharField(blank=True, max_length=8)
    # TODO: add other neeeded fields

    # [DONE] club name
    # [DONE] club motto
    # [DONE: IN CALENDAR]club location
    # [DONE] club schedule
    # [DONE] club profile picture
    # [DONE: IN TAGS] club main category
    # [DONE] club tags
    # [DONE] club social media URLs
    # [DONE] club description
    # [DONE] club gallery/images bank
    # club execs list
    # a. club exec profile picture
    # b. club exec position
    # [DONE] club google classroom code

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
    description = models.TextField(blank=True, max_length=500)

    def save(self):
        super().save()
        
        img = Image.open(self.image.path)
        
        if img.height > 300 or img.width > 300:
            output_size = (300, 300)
            img.thumbnail(output_size)
            img.save(self.image.path)

class ClubSocialMedia(models.Model):
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

    club = models.ForeignKey(Club, related_name='socialMedia', on_delete=models.CASCADE) 
    site = models.CharField(
        max_length=2,
        choices=Sites.choices,
        default=Sites.OTHER
    )
