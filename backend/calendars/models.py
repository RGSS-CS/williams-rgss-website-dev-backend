from django.db import models
#from django_ical.utils import build_rrule_from_recurrences_rrule
from django.conf import settings
from django.utils import timezone
#from clubs.models import Club
from django.urls import reverse
from clubs.models import Club

class Calendar(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    product_id = settings.CALENDAR_PRODUCT_ID
    timezone = models.TextField(default="UTC") # TODO: deal w/ this later, possibly choices?
    filename = models.TextField(default="invalid")
    club = models.OneToOneField(Club, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        if self.filename and not self.filename.endswith(".ics"):
            self.filename += ".ics"

        super().save(*args, **kwargs)

class CalendarEvent(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    start = models.DateTimeField()
    end = models.DateTimeField()
    location = models.CharField(max_length=255, blank=True)
    created = models.DateTimeField(default=timezone.now)
    updated = models.DateTimeField(default=timezone.now)
    calendar = models.ForeignKey(Calendar, on_delete=models.CASCADE)

    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse("calendars_get_calendar_event", kwargs={"event": self.title})
    
