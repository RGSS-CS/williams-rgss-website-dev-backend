from django.db import models
from solo.models import SingletonModel


class Ticker(models.Model):
    item = models.CharField(help_text='This should be a short announcement that rotates on the ticker bar at the homepage.')

    class Meta:
        verbose_name = 'Ticker Bar Items'
        verbose_name_plural = 'Ticker Bar Items'

    def __str__(self):
        return(self.item)

class STUCO(SingletonModel):
    council_name = models.CharField(default="STUCO", max_length=10, help_text="The name of the council (e.g, SAC)")
    group_photo = models.ImageField(blank=True, null=True, upload_to='upload/stuco/')

    class Meta: 
        verbose_name = 'Student Council Settings'
        verbose_name_plural = 'Student Council Settings'

    def __str__(self):
        return('')