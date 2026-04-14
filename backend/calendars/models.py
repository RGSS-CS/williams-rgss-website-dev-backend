from django.db import models
from clubs.models import Club

class Calendar(models.Model):
    club = models.ForeignKey(Club, on_delete=models.CASCADE, related_name='profile')
    name = models.CharField(max_length=100)
    description = models.TextField()
