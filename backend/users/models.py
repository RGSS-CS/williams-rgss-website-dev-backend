from django.db import models
from django.utils import timezone
from django.utils.crypto import get_random_string

def get_random_code():
    return get_random_string(length=32)

class UserJoinCode(models.Model):
    code = models.CharField(default=get_random_code, unique=True, verbose_name="Security Code")
    label = models.CharField(max_length=50, blank=True, verbose_name="Title", help_text="A easily identifiable name for this qr code, e.g. 'Cafeteria'")
    description = models.TextField(blank=True, max_length=300, help_text="A description of this qr code, e.g. 'For use in the cafeteria only.' (*NOT REQUIRED)")
    expiry = models.DateTimeField(null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    enabled = models.BooleanField(default=True)
    max_uses = models.PositiveBigIntegerField(blank=True, null=True)
    uses = models.PositiveBigIntegerField(default=0)

    class Meta:
        verbose_name = "Student Registration QR Code"

    def is_expired(self) -> bool:
        if self.expiry is None:
            return False
        return self.expiry <= timezone.now()

    def exceeded_max_uses(self) -> bool:
        if self.max_uses is None:
            return False
        return self.uses >= self.max_uses

    def __str__(self) -> str:
        return self.label