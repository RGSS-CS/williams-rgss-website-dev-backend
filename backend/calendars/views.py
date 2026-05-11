from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from datetime import datetime
from django_ical.utils import build_rrule_from_recurrences_rrule
from django_ical.views import ICalFeed
from .models import Calendar, CalendarEvent
from rest_framework import viewsets
from .serializers import CalendarSerializer, CalendarEventSerializer

class CalendarFeed(ICalFeed):
    product_id = '-//example.com//Example//EN'
    timezone = 'UTC'
    file_name = "event.ics"

    def get_object(self, request, *args, **kwargs):
        return get_object_or_404(Calendar, pk=kwargs.get("pk"))

    def items(self, calendar):
        # calendar = get_object_or_404(Calendar, filename=self.kwargs.get("calendar"))
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

def get_calendar_event(request, *args, **kwargs):
    return JsonResponse("hi, this isn't implemented yet. how the heck did u find this?")

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

class CalendarViewSet(viewsets.ModelViewSet):
    queryset = Calendar.objects.all()
    serializer_class = CalendarSerializer

class CalendarEventViewSet(viewsets.ModelViewSet):
    queryset = CalendarEvent.objects.all()
    serializer_class = CalendarEventSerializer
