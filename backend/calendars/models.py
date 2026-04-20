from django.db import models
from django.contrib.syndication.views import Feed
from django_ical.utils import build_rrule_from_recurrences_rrule
from django_ical.views import ICalFeed
from django.conf import settings
from django.utils import timezone
#from clubs.models import Club

class Calendar(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    product_id = settings.CALENDAR_PRODUCT_ID
    timezone = models.TextField(default="UTC") # TODO: deal w/ this later, possibly choices?

    # def save(self, *args, **kwargs):
    #     if self.description and not self.description.startswith(settings.CALENDAR_PRODUCT_ID):
    #         self.description = settings.CALENDAR_PATH + self.description
    #     super().save(*args, **kwargs)

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
