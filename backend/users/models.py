from django.db import models
from django.utils import timezone

class UserJoinCode(models.Model):
    code = models.CharField()
    label = models.CharField()
    description = models.TextField(blank=True)
    expiry = models.DateTimeField(null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    enabled = models.BooleanField(default=True)
    max_uses = models.PositiveBigIntegerField(blank=True, null=True)
    uses = models.PositiveBigIntegerField(default=0)

    def is_expired(self) -> bool:
        if self.expiry and self.expiry > timezone.now():
            return True
        
    def exceeded_max_uses(self) -> bool:
        if self.uses >= self.max_uses:
            return True
