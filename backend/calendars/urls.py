from django.urls import path, include, re_path
from . import views

urlpatterns = [
    # path('admin/', admin.site.urls),
    path("ical/<int:pk>/", views.CalendarFeed(), name="calendars_calendarfeed"),
    path("event/<int:pk>/", views.get_calendar_event, name="calendars_get_calendar_event")
   # path("events/", views.get_events)
]
