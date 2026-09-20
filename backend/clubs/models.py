from django.db import models
from django.utils import timezone
from taggit.managers import TaggableManager
from PIL import Image
from django.contrib.contenttypes.fields import GenericRelation

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

    visible = models.BooleanField(default=True, help_text='Is it visible to the public?')

    name = models.CharField(
        max_length=100, unique=True, help_text="Insert the Name of your club"
    )
    preview_description = models.TextField(
        null=True, max_length=200, 
        help_text="Insert a small description for your club. The long description is filled below."
    )
    description = models.TextField(
        null=True, max_length=500, 
        help_text="Insert a long description for your club. This is where you can describe your club in detail."
    )
    category = TaggableManager(blank=True)
    repetition = models.CharField(
        null=True, max_length=10, choices=Repetition.choices, 
        help_text="How often does your club meet? If your club meets on a different schedule," \
        " please select 'Weekly' and specify in the description."
    )
    classroom_code = models.CharField(
        max_length=10, null=True, blank=True,
        help_text="This does not need an input if there is no google classroom code. "
        "*It will not be visible when selected 'Not Accepting' in the field below."
    )
    accepting_applicants = models.CharField(
        null=True, max_length=16, choices=AcceptingApplications.choices, 
        help_text="Select 'Accepting' if applications are required. Select 'Open To Everyone' for google classroom code"
    )
    application_form_link = models.URLField(
        blank=True, null=True, max_length=250, 
        help_text="This can be either a google classroom invite link or a application" \
        " form link *It will not be visible when selected 'Not Accepting' in the field below."
    )
    day_of_meeting = models.CharField(max_length=10, choices=WeekDay.choices, null=True)
    time = models.TimeField(null=True)
    location = models.CharField(null=True, blank=True, help_text='A room number or general name of the location.')
    teacher_advisor = models.CharField(
        max_length=20, help_text="Please insert the name of the teacher. " \
        "Please insert Mr./Mrs./Ms. , followed by the last name"
    )
    tagline = models.CharField(
        blank=True, null=True, max_length=30, 
        help_text="The tagline is the title about your club. Make it intruiging such as" \
        " 'A community of curious minds'"
    )
    join_instructions = models.TextField(
        default="Use the google classroom code or application form link to join.", max_length=500, 
        help_text="This is where you tell the students how to join, such as " \
        "using a google classroom code or a link to a form. *It will not be " \
        "visible when selected 'Not Accepting' in the field below."
    )

    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

class ClubWhyJoin(models.Model):
    club = models.ForeignKey(
        Club, on_delete=models.CASCADE, related_name="why_join_reasons"
    )
    title = models.CharField(
        max_length=30, help_text="Insert a title for your reason to join the club."
    )
    description = models.TextField(
        max_length=300, 
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
    
class ClubAnnouncement(models.Model):
    title = models.CharField(max_length=200, null=True)
    description = models.TextField(max_length=500, null=True)
    date_posted = models.DateTimeField(default=timezone.now, help_text="This does not reflect the post status of the announcement, it only reads the current date/time.")
    popup = models.BooleanField(default=False, help_text="Determines whether popup is enabled for this announcement. Regardless, it will be shown in the announcements section.")
    expiry = models.DateTimeField(null=True, help_text="When does this post expire? When expired, it will be marked as resolved in the announcment section.")
    club = models.ForeignKey(Club, on_delete=models.CASCADE, related_name="club_announcement")

    class Meta:
        verbose_name =  "Club Announcement"
        verbose_name_plural = "Club Announcement"

    def __str__(self):
        return self.title
