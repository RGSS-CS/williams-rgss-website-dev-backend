from django import forms
from django.contrib import admin

from photologue.admin import GalleryAdmin as GalleryAdminDefault
from photologue.models import Gallery

from clubs.models import GalleryExtended

class GalleryExtendedInline(admin.StackedInline):
    model = GalleryExtended
    can_delete = False

class GalleryAdminForm(forms.ModelForm):
    class Meta:
        model = Gallery
        exclude = []
        

class GalleryAdmin(GalleryAdminDefault):
    form = GalleryAdminForm

    """Define our new one-to-one model as an inline of Photologue's Gallery model."""

    inlines = [GalleryExtendedInline, ]

admin.site.unregister(Gallery)
admin.site.register(Gallery, GalleryAdmin)