from django.contrib import admin
from .models import Calendar, CalendarEvent, CalendarSettings
from solo.admin import SingletonModelAdmin

admin.site.register(CalendarSettings, SingletonModelAdmin)
admin.site.register(Calendar)
admin.site.register(CalendarEvent)
