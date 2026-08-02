from django.db import models

class UserJoinCode(models.Model):
    code = models.CharField(required=True)
    label = models.CharField(required=True)
    description = models.TextField()
    expiry = models.DateTimeField(required=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
