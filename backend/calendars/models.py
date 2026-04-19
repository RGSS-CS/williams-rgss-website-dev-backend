from django.db import models
from clubs.models import Club

class Calendar(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()

