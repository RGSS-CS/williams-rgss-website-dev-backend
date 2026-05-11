from django.urls import path, include, re_path
from . import views
from rest_framework.routers import DefaultRouter

calendarRouter = DefaultRouter()
calendarRouter.register("json/", views.CalendarViewSet)

eventRouter = DefaultRouter()
eventRouter.register("", views.CalendarEventViewSet)

urlpatterns = [
    # path('admin/', admin.site.urls),
    path("calendar/ical/<int:pk>/", views.CalendarFeed(), name="calendars_calendarfeed"),
    path("calendar/", include(calendarRouter.urls)),
    path("event/", include(eventRouter.urls), name="calendars_get_calendar_event")
   # path("events/", views.get_events)
]
