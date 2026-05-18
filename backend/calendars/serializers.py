from rest_framework import serializers
from .models import Calendar, CalendarEvent
from clubs.models import Club

class CalendarEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = CalendarEvent
        fields = ["id", "title", "description", "start", "end", "location", "created", "updated", "calendar_id"]

class CalendarSerializer(serializers.ModelSerializer):
    calendarevents = CalendarEventSerializer(many=True, read_only=True)

    class Meta:
        model = Calendar
        fields = ["id", "name", "description", "timezone", "filename", "calendarevents", "club_id"]
