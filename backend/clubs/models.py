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
        NOTIFIED = "NOTIFIED", "Notified"

    class AcceptingApplications(models.TextChoices):
        ACCEPTING = "AC", "Accepting"
        NOT_ACCEPTING = "WA", "Not Accepting"
        OPEN_TO_EVERYONE = "OE", "Open To Everyone"

    #group = models.OneToOneField(Group, on_delete=models.CASCADE, related_name='group')
    name = models.CharField(
        max_length=100, help_text="Insert the Name of your club"
    )
    preview_description = models.TextField(
        blank=True, max_length=200, 
        help_text="Insert a small description for your club. The long description is filled below."
    )
    description = models.TextField(
        blank=True, max_length=500, 
        help_text="Insert a long description for your club. This is where you can describe your club in detail."
    )
    category = TaggableManager()
    repetition = models.CharField(blank=True, max_length=10, choices=Repetition.choices, help_text="How often does your club meet? If your club meets on a different schedule, please select 'Weekly' and specify in the description.")
    image = models.ImageField(default="clubs/default.png", upload_to=get_upload_path_club)
    classroom_code = models.CharField(blank=True, max_length=10, null=True, help_text="This does not need an input if there is no google classroom code. *It will not be visable when selected 'Not Accepting' in the field below.")
    accepting_applicants = models.CharField(blank=True, max_length=16, choices=AcceptingApplications.choices, help_text="Select 'Accepting' if applications are required. Select 'Open To Everyone' for google classroom code")
    application_form_link = models.URLField(blank=True, max_length=250, help_text="This can be either a google classroom invite link or a application form link *It will not be visable when selected 'Not Accepting' in the field below.")
    announcement = models.CharField(null=True, help_text="This is where you announce application news.") #BEN ISSUE
    day_of_meeting = models.CharField(max_length=10, choices=WeekDay.choices, blank=True)
    time = models.TimeField(blank=True, null=True)
    room_number = models.PositiveIntegerField(blank=True, null=True)
    teacher_advisor = models.CharField(blank=True, max_length=20, help_text="Please insert the name of the teacher. Please insert Mr./Mrs./Ms. , followed by the last name")
    tagline = models.CharField(blank=True, max_length=30, help_text="The tagline is the title about your club. Make it intruiging such as 'A community of curious minds'")
    join_instructions = models.TextField(default="Use the google classroom code or application form link to join.", max_length=500, help_text="This is where you tell the students how to join, such as using a google classroom code or a link to a form. *It will not be visable when selected 'Not Accepting' in the field below.")
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

class ClubWhyJoin(models.Model):
    club = models.ForeignKey(
        Club, on_delete=models.CASCADE, related_name="why_join_reasons"
    )
    title = models.CharField(
        max_length=200, help_text="Insert a title for your reason to join the club."
    )
    description = models.TextField(
        max_length=2000, 
        help_text="Insert a detailed description for your reason to join the club."
    )
    index = models.IntegerField(
        help_text="The order in which this reason will be displayed."
    )

    class Meta:
        verbose_name =  "Why Join"
        verbose_name_plural = "Why Join"
        ordering = ["index"]

    def __str__(self):
        return self.title
    
    # def save(self, *args, **kwargs):
    #     if ClubWhyJoin.objects.filter(index=self.index).count() > 1:
    #         for i in ClubWhyJoin.objects.filter(index__gt=self.index):
    #             i.index += 1
    #             i.save()

    #     super().save(*args, **kwargs)
        

class ClubAnnouncement(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(max_length=2000)
    date_posted = models.DateTimeField(default=timezone.now)
    pinned = models.BooleanField(
        default=False,
        help_text="Whether or not the post should be pinned to the top of the page."
    )
    club = models.ForeignKey(
        Club, on_delete=models.CASCADE, related_name="club_announcement"
    )

    class Meta:
        verbose_name =  "Club Announcement"
        verbose_name_plural = "Club Announcement"

    def __str__(self):
        return self.title

class ClubGalleryImage(models.Model):
    name = models.CharField(max_length=100)
    category = TaggableManager(blank=True)
    description = models.TextField(blank=True, max_length=500)
    image = models.ImageField(upload_to=get_upload_path_club_gallery)
    club = models.ForeignKey(
        Club, related_name='galleryImage', on_delete=models.CASCADE
    )
    
    def save(self):
        super().save()
        
        img = Image.open(self.image.path)
        
        if img.height > 300 or img.width > 300:
            output_size = (300, 300)
            img.thumbnail(output_size)
            img.save(self.image.path)
