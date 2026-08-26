from django.db import models
from django.utils import timezone
from django.conf import settings
from taggit.managers import TaggableManager
from PIL import Image
from management.models import SocialMedia
from django.contrib.contenttypes.fields import GenericRelation
from photologue.models import Gallery

class GalleryExtended(models.Model):
    gallery = models.OneToOneField(
        Gallery, null=True, blank=True, on_delete=models.SET_NULL,
        related_name="club", help_text="The photo gallery for this club."
        )

    tags = TaggableManager(blank=True)
    class Meta: 
        verbose_name = "Extra Fields"

    def __str__(self):
        return self.gallery.title

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

    name = models.CharField(
        max_length=100, help_text="Insert the Name of your club"
    )
    preview_description = models.TextField(
        null=True, max_length=200, 
        help_text="Insert a small description for your club. The long description is filled below."
    )
    description = models.TextField(
        null=True, max_length=500, 
        help_text="Insert a long description for your club. This is where you can describe your club in detail."
    )
    category = TaggableManager()
    repetition = models.CharField(null=True, max_length=10, choices=Repetition.choices, help_text="How often does your club meet? If your club meets on a different schedule, please select 'Weekly' and specify in the description.")
    classroom_code = models.CharField(max_length=10, null=True, help_text="This does not need an input if there is no google classroom code. *It will not be visable when selected 'Not Accepting' in the field below.")
    accepting_applicants = models.CharField(null=True, max_length=16, choices=AcceptingApplications.choices, help_text="Select 'Accepting' if applications are required. Select 'Open To Everyone' for google classroom code")
    application_form_link = models.URLField(blank=True, null=True, max_length=250, help_text="This can be either a google classroom invite link or a application form link *It will not be visable when selected 'Not Accepting' in the field below.")
    announcement = models.CharField(null=True, help_text="This is where you announce application news.") #BEN ISSUE
    day_of_meeting = models.CharField(max_length=10, choices=WeekDay.choices, null=True)
    time = models.TimeField(null=True)
    room_number = models.PositiveIntegerField(null=True)
    teacher_advisor = models.CharField(max_length=20, help_text="Please insert the name of the teacher. Please insert Mr./Mrs./Ms. , followed by the last name")
    tagline = models.CharField(blank=True, null=True, max_length=30, help_text="The tagline is the title about your club. Make it intruiging such as 'A community of curious minds'")
    join_instructions = models.TextField(null=True, default="Use the google classroom code or application form link to join.", max_length=500, help_text="This is where you tell the students how to join, such as using a google classroom code or a link to a form. *It will not be visable when selected 'Not Accepting' in the field below.")
    social_media = GenericRelation(SocialMedia)
    gallery = models.ForeignKey(Gallery, on_delete=models.SET_NULL, null=True, blank=True, related_name="clubs",)

    PENDING_APPROVAL_FIELDS = [
        "name", "preview_description", "description", "tagline",
        "repetition", "classroom_code", "accepting_applicants",
        "application_form_link", "announcement", "day_of_meeting", "time",
        "room_number", "teacher_advisor", "join_instructions",
    ]

    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)


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
    

    ################# USER ACCESS CONTROLS ####################

class ClubMembership(models.Model):
    class Role(models.TextChoices):
        EXECUTIVE = "EXC", "Club Executive"
        CLUB_ADMIN = "ADM", "Club Administrator"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='club_memberships')
    club = models.ForeignKey(Club, on_delete=models.CASCADE, related_name="memberships")
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.EXECUTIVE)
    bypass_confirmation_restrictions = models.BooleanField(default=False, help_text="This allows execs to publish changes without approval by the club administrator")

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Club Executive Membership"
        verbose_name_plural = "Club Executive Memberships"

        constraints = [
            models.UniqueConstraint(fields=['user', 'club'], name='unique_club_membership')
        ]

    def __str__(self) -> str:
        return f"{self.user} - {self.club} ({self.get_role_display()})"

    def save(self, *args, **kwargs):
        if self.role != self.Role.EXECUTIVE:
            self.bypass_confirmation_restrictions = False

        super().save(*args, **kwargs)

class ClubChanges(models.Model):
    class ApprovalStatus(models.TextChoices):
        PENDING = "PND", "Pending Approval"
        APPROVED = "APR", "Approved"
        REJECTED = "RJC", "Rejected"

    club = models.ForeignKey(Club, on_delete=models.CASCADE, related_name='pending_edits')
    changes = models.JSONField(help_text="Changed Value")
    status = models.CharField(max_length=10, choices=ApprovalStatus.choices, default= ApprovalStatus.PENDING)
    submitted_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='submitted_changes')
    submitted_at = models.DateTimeField(auto_now_add=True)
    reviewed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, default ="Pending Reviewer", related_name='reviewed_club_changes')
    reviewed_at = models.DateTimeField(null=True, blank = True)
    review_note = models.TextField(max_length=200, blank=True)

    def __str__(self) -> str:
        return f"Changes for {self.club} ({self.get_status_display()})"

    def approve(self, reviewer, note=""):
        allowed = set(Club.PENDING_APPROVAL_FIELDS)
        for field, value in self.changes.items():
            if field in allowed:
                setattr(self.club, field, value)
        self.club.save()

        self.status = self.ApprovalStatus.APPROVED
        self.reviewed_by = reviewer
        self.reviewed_at = timezone.now()
        self.review_note = note
        self.save()

    def reject(self, reviewer, note=""):
        self.status = self.ApprovalStatus.REJECTED
        self.reviewed_by = reviewer
        self.reviewed_at = timezone.now()
        self.review_note = note
        self.save()