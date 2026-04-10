from django.db import models
from django.utils import timezone
from django.contrib.auth.models import Group

class Club(models.Model):
    group = models.OneToOneField(Group, on_delete=models.CASCADE, related_name='profile')
    name = models.CharField(max_length=100)
    description = models.TextField()
    date_posted = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name
