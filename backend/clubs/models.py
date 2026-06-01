from django.db import models
from django.utils import timezone
from taggit.managers import TaggableManager
from PIL import Image
from management.models import SocialMedia
from django.contrib.contenttypes.fields import GenericRelation

def get_upload_path_club(instance, filename):
    upload_to = f"clubs/{instance.club.pk}/"
    ext = filename.split('.')[-1]
    filename = f"{upload_to}{instance.club.pk}.{ext}"
    return filename

class Club(models.Model):
    class WeekDay(models.TextChoices):
        MONDAY = "MONDAY", "Monday"
        TUESDAY = "TUESDAY", "Tuesday"
        WEDNESDAY = "WEDNESDAY", "Wednesday"
        THURSDAY = "THURSDAY", "Thursday"
        FRIDAY = "FRIDAY", "Friday"

    class Repetition(models.TextChoices):
        WEEKLY = "WEEKLY", "Weekly"
        BIWEEKLY = "BIWEEKLY", "Biweekly"
        MONTHLY = "MONTHLY", "Monthly"

    #group = models.OneToOneField(Group, on_delete=models.CASCADE, related_name='group')
    name = models.CharField(max_length=100)
    preview_description = models.CharField(blank=True, max_length=200)
    description = models.TextField(blank=True, max_length=500)
    category = TaggableManager()
    repetition = models.CharField(blank=True, max_length=10, choices=Repetition.choices)
    image = models.ImageField(default="clubs/default.png", upload_to=get_upload_path_club)
    classroom_code = models.CharField(blank=True, max_length=10)
    day_of_meeting = models.CharField(max_length=10, choices=WeekDay.choices, blank=True)
    time = models.TimeField(blank=True, null=True)
    room_num = models.IntegerField(blank=True, null=True)
    teacher_advisor = models.CharField(blank=True, max_length=20)
    social_media = GenericRelation(SocialMedia)

    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        
        img = Image.open(self.image.path)
        
        if img.height > 300 or img.width > 300:
            output_size = (300, 300)
            img.thumbnail(output_size)
            img.save(self.image.path)

def get_upload_path_club_gallery(instance, filename):
    upload_to = f"clubs/{instance.club.pk}/gallery/"
    filename = f"{upload_to}{filename}"
    return filename

def get_upload_path(*args, **kwargs): # fix migration errors
    return get_upload_path_club_gallery(*args, **kwargs)


class ClubGalleryImage(models.Model):
    club = models.ForeignKey(Club, related_name='galleryImage', on_delete=models.CASCADE)
    image = models.ImageField(upload_to=get_upload_path_club_gallery)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, max_length=500)
    category = TaggableManager(blank=True)
    
    def save(self):
        super().save()
        
        img = Image.open(self.image.path)
        
        if img.height > 300 or img.width > 300:
            output_size = (300, 300)
            img.thumbnail(output_size)
            img.save(self.image.path)
