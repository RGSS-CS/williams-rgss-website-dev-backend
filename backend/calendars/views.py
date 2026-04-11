from django.http import HttpResponse
from django.utils import timezone
from icalendar import Calendar, Event as ICalEvent
from .models import School_event

def ical_feed(request):
    cal = Calendar()
    cal.add("prodid", "-//demo//School Events//EN")
    cal.add("version", "2.0")

    for obj in School_event.objects.select_related("club").all():
        event = ICalEvent()
        event.add("uid", f"{obj.id}@demo.com")
        event.add("summary", obj.title)

        full_description = (
            f"{obj.description}\n\n"
            f"Club: {obj.club.name}\n"
            f"Meeting Day: {obj.club.day.capitalize()}\n"
            f"Classroom Code: {obj.club.classroom_code}\n"
            f"Club Description: {obj.club.description}"
        )

        event.add("description", full_description)
        event.add("dtstart", obj.start_time)
        event.add("dtend", obj.end_time)
        event.add("dtstamp", timezone.now())

        event.add("categories", [obj.club.name])

        cal.add_component(event)

    response = HttpResponse(cal.to_ical(), content_type="text/calendar")
    response["Content-Disposition"] = 'attachment; filename=\"school_events.ics\"'
    return response
