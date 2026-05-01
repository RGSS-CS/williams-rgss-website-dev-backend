from django.db import models
from django.utils import timezone
from django.contrib.auth.models import Group
from taggit.managers import TaggableManager

class Club(models.Model):
    #group = models.OneToOneField(Group, on_delete=models.CASCADE, related_name='group')
    name = models.CharField(max_length=100)
    description = models.TextField(default="", max_length=500)
    tags = TaggableManager()
    
    # TODO: add other neeeded fields

    def __str__(self):
        return self.name
