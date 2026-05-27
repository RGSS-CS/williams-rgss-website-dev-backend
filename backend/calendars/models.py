from django.db import models
#from django_ical.utils import build_rrule_from_recurrences_rrule
from django.conf import settings
from django.utils import timezone
from django.urls import reverse
from clubs.models import Club
from solo.models import SingletonModel

class CalendarSettings(SingletonModel):
    vendor = models.CharField(default="SCHOOL", max_length=50)
    product = models.CharField(default="StuCo Website", max_length=50)
    language = models.CharField(default="EN", max_length=2)

    def __str__(self):
        return "Calendar Configuration"

    class Meta:
        verbose_name = "Calendar Configuration"

class Calendar(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    timezone = models.TextField(default="america/toronto") # TODO: deal w/ this later, possibly choices? maybe?
    filename = models.TextField(default=f"{name}.ics")
    club = models.OneToOneField(Club, on_delete=models.CASCADE, blank=True, null=True)

    def save(self, *args, **kwargs):
        if self.filename and not self.filename.endswith(".ics"):
            self.filename += ".ics"

        super().save(*args, **kwargs)

class CalendarEvent(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True, max_length=500)
    start = models.DateTimeField()
    end = models.DateTimeField()
    location = models.CharField(max_length=255, blank=True)
    created = models.DateTimeField(default=timezone.now)
    updated = models.DateTimeField(default=timezone.now)
    calendar = models.ForeignKey(Calendar, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse("calendarevent-detail", kwargs={"pk": self.pk})
    
