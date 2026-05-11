from rest_framework import serializers
from .models import Calendar, CalendarEvent

class CalendarEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = CalendarEvent
        fields = ["title", "description", "start", "end", "location", "created", "updated", "calendar.pk"]

class CalendarSerializer(serializers.ModelSerializer):
    calendarevents = CalendarEventSerializer(many=True, read_only=True)

    class Meta:
        model = Calendar
        fields = ["name", "description", "timezone", "filename", "club.pk", "calendarevents"]
