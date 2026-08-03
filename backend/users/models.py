from django.db import models

class UserJoinCode(models.Model):
    code = models.CharField()
    label = models.CharField()
    description = models.TextField()
    expiry = models.DateTimeField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
