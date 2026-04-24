from django.contrib import admin
from django.urls import path, include, re_path
from . import views

urlpatterns = [
    # path('admin/', admin.site.urls),
    path("get/ical/<str:calendar>/", views.CalendarFeed(), name="calendars_calendarfeed"),
    path("get/ical/<str:event>/", views.get_calendar_event, name="calendars_get_calendar_event")
   # path("events/", views.get_events)
]
