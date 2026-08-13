from django import forms
from django.contrib import admin
from django.utils.safestring import mark_safe
from photologue.admin import GalleryAdmin as GalleryAdminDefault
from photologue.admin import PhotoAdmin as PhotoAdminDefault
from photologue.models import Gallery, Photo

from clubs.models import GalleryExtended

class GalleryExtendedInline(admin.StackedInline):
    model = GalleryExtended
    can_delete = False

class GalleryAdminForm(forms.ModelForm):
    class Meta:
        model = Gallery
        exclude = ['sites','is_public']
        

class PhotoAdminForm(forms.ModelForm):
    class Meta: 
        model = Photo
        exclude = ['is_public', 'sites']
        widgets = {
            "caption": forms.Textarea(attrs={"rows": 1, "cols": 80}),
        }

class GalleryAdmin(GalleryAdminDefault):
    form = GalleryAdminForm
    inlines = [GalleryExtendedInline, ]
    view_on_site = False

admin.site.unregister(Gallery)
admin.site.register(Gallery, GalleryAdmin)


class PhotoAdmin(PhotoAdminDefault):
    form = PhotoAdminForm
    view_on_site = False

    def admin_thumbnail_safe(self, obj):
        thumb_url = obj.get_admin_thumbnail_url() if hasattr(obj, "get_admin_thumbnail_url") else obj.image.url
        return mark_safe(f'<a href="{obj.image.url}"><img src="{thumb_url}"></a>')
    admin_thumbnail_safe.short_description = "Thumbnail"

admin.site.unregister(Photo)
admin.site.register(Photo, PhotoAdmin)