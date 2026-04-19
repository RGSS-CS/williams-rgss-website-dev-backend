from django.db import models
#from clubs.models import Club

class Calendar(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    product_id = "" # TODO: deal w/ this later
    timezone = models.TextField("UTC") # TODO: deal w/ this later, possibly choices?
