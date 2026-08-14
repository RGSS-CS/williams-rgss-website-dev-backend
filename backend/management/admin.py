from django.contrib import admin
from django.contrib.contenttypes.admin import GenericStackedInline
from solo.admin import SingletonModelAdmin
from image_cropping import ImageCroppingMixin
from django.forms import TextInput, Textarea
from django.db import models
from django import forms

from .forms import LocationAdminForm
from .models import Location, SiteSettings, PageSettings


class LocationInline(GenericStackedInline):
    """
    Always-present single location inline on SiteSettings.

    - min_num=1, max_num=1, extra=0: exactly one location row, always.
    - can_delete=False: prevents removing the location entry entirely.
    - The LeafletPickerWidget renders the map; lat/lon are read-only in JS.
    """
    model = Location
    form = LocationAdminForm
    min_num = 1
    max_num = 1
    extra = 0
    can_delete = False
    verbose_name = "School Location"
    verbose_name_plural = "School Location"


class SiteSettingsAdminForm(forms.ModelForm):
    captcha = forms.MultipleChoiceField(
        choices=SiteSettings.CaptchaChoice.choices,
        widget=forms.CheckboxSelectMultiple,
        required=False,
    )

    class Meta:
        model = SiteSettings
        fields = [
            'maintainance_mode','frontend_url', 'school_name','council_name',
            'school_email', 'school_phone', 'favicon', 'favicon_cropping',
            'stuco_image', 'about_stuco', 'about_school', 'school_mascot',
            'school_primary_color', 'school_secondary_color', 'school_tertiary_color',
            'captcha',
        ]

@admin.register(SiteSettings)
class SiteSettingsAdmin(ImageCroppingMixin, SingletonModelAdmin):
    forms = SiteSettingsAdminForm
    inlines = [LocationInline]

@admin.register(PageSettings)
class PageSettingsAdmin(admin.ModelAdmin):
    exclude = ("internal_site_name",)
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows': 4, 'cols': 60})},
    }
    def has_add_permission(self, request):
        """Disables the add button in admin"""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Disables the delete button in admin"""
        return False
