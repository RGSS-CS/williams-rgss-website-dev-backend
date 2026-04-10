from django.shortcuts import render
from django.http import HttpResponse
from datetime import datetime
from gcsa.google_calendar import GoogleCalendar
import json

calendar = GoogleCalendar()

# Create your views here.
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
