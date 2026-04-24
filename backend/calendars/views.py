from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from datetime import datetime
from django_ical.utils import build_rrule_from_recurrences_rrule
from django_ical.views import ICalFeed
from .models import Calendar, CalendarEvent

class CalendarFeed(ICalFeed):
    product_id = '-//example.com//Example//EN'
    timezone = 'UTC'
    file_name = "event.ics"

    def __init__(self, **kwargs):
        self.kwargs = kwargs
        super().__init__()

    def items(self):
        # calendar = get_object_or_404(Calendar, filename=self.kwargs.get("calendar"))
        calendar = get_object_or_404(Calendar, filename="test.ics")
        return CalendarEvent.objects.filter(calendar=calendar).order_by('-start')

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return item.description

    def item_start_datetime(self, item):
        return item.start
    
    ####################################################
    ### Reoccurence TODO: implement later

    # def item_rrule(self, item):
    #     if item.recurrences:
    #         rules = []
    #         for rule in item.recurrences.rrules:
    #             rules.append(build_rrule_from_recurrences_rrule(rule))
    #         return rules

    # def item_exrule(self, item):
    #     if item.recurrences:
    #         rules = []
    #         for rule in item.recurrences.exrules:
    #             rules.append(build_rrule_from_recurrences_rrule(rule))
    #         return rules

    # def item_rdate(self, item):
    #     if item.recurrences:
    #         return item.recurrences.rdates

    # def item_exdate(self, item):
    #     if item.recurrences:
    #         return item.recurrences.exdates

    ####################################################

def get_calendar_event(request):
    return HttpResponse("hi")

#REQRUIRE NEW METHOD, django-ical
'''
def get_events(request):
    time_min = datetime.fromtimestamp(request.POST.get("timestamp_start"))
    time_max = datetime.fromtimestamp(request.POST.get("timestamp_end"))

    events = []
    for i in GoogleCalendar.get_events(time_min, time_max, order_by="startTime"):
        events.append({
            "start": i.start,
            "end": i.end,
            "timezone": i.timezone,
            "event_id": i.event_id,
            "description": i.description,
            "location": i.location,
            "color_id": i.color_id
        })
    
    return HttpResponse(json.dumps(events))
'''
