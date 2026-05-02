from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from .models import Club
from calendars.models import Calendar

def club_info(request, *args, **kwargs):
    club = get_object_or_404(Club, pk=kwargs["pk"])
    club_data = {
        "pk": club.pk,
        "name": club.name,
        "description": club.description,
        "calendar": club.calendar.pk
    }

    return JsonResponse(club_data)
