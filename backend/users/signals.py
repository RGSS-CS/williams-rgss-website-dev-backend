from django.apps import AppConfig
from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.contrib.auth.models import Group, Permission

GROUPS = {
    "Public Verified User" : [],
    "Club Executive" : [
                
    ]
}