from django.contrib import admin
from solo.admin import SingletonModelAdmin
from .models import SiteSettings, PageSettings

admin.site.register(SiteSettings, SingletonModelAdmin)

@admin.register(PageSettings)
class PageSettingsAdmin(admin.ModelAdmin):

    def has_add_permission(self, request):
        """Disables the add button in admin"""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Disables the delete button in admin"""
        return False
