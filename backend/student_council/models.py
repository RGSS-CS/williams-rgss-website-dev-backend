from django.db import models
from solo.models import SingletonModel

class SchoolAnnouncements(models.Model):
    title = models.CharField(help_text='The title of the announcement')
    contents = models.TextField(null=True, help_text='The contents of the announcement')
    date_posted = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class Announcements(SingletonModel):
    ticker_items = models.TextField(blank=True, null=True, help_text='Every newline represents a new object.', max_length=500)

    class Meta:
        verbose_name = 'Announcement Objects'
        verbose_name_plural = 'Announcement Objects'

    def __str__(self):
        return('')

    
class STUCO(SingletonModel):
    council_name = models.CharField(default="STUCO", max_length=10, help_text="The name of the council (e.g, SAC)")
    group_photo = models.ImageField(blank=True, null=True, upload_to='upload/stuco/')
    photo_caption = models.TextField(blank=True, null=True, help_text='A legend for the people present in the photo.')

    class Meta: 
        verbose_name = 'Student Council Settings'
        verbose_name_plural = 'Student Council Settings'

    def __str__(self):
        return('')