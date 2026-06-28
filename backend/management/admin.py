from django.contrib import admin
from django.contrib.contenttypes.admin import GenericStackedInline
from solo.admin import SingletonModelAdmin

from .forms import LocationAdminForm
from .models import Location, SiteSettings


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


@admin.register(SiteSettings)
class SiteSettingsAdmin(SingletonModelAdmin):
    inlines = [LocationInline]