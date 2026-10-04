from datetime import timedelta
from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from icalendar import Calendar as ICalendar

from clubs.models import Club
from .models import Calendar, CalendarEvent, CalendarSettings


class CalendarTests(TestCase):
    def setUp(self):
        revalidation = patch('requests.post')
        revalidation.start()
        self.addCleanup(revalidation.stop)

    def test_filename_extension_is_added_only_once(self):
        for filename in ('school', 'school.ics'):
            with self.subTest(filename=filename):
                calendar = Calendar.objects.create(name='School', filename=filename)
                calendar.save()
                calendar.refresh_from_db()
                self.assertEqual(calendar.filename, 'school.ics')

    def test_creating_and_updating_club_creates_only_one_calendar(self):
        club = Club.objects.create(name='Chess')
        calendar = Calendar.objects.get(club=club)
        self.assertEqual(calendar.name, 'Chess')
        club.description = 'Weekly games'
        club.save()
        self.assertEqual(Calendar.objects.filter(club=club).count(), 1)

    def test_deleting_club_cascades_to_calendar_and_events(self):
        club = Club.objects.create(name='Chess')
        calendar = Calendar.objects.get(club=club)
        event = CalendarEvent.objects.create(
            calendar=calendar, title='Meeting', start=timezone.now(), end=timezone.now()
        )
        club.delete()
        self.assertFalse(Calendar.objects.filter(pk=calendar.pk).exists())
        self.assertFalse(CalendarEvent.objects.filter(pk=event.pk).exists())


class CalendarFeedTests(TestCase):
    def setUp(self):
        self.calendar = Calendar.objects.create(
            name='School', filename='school.ics', timezone='America/Toronto'
        )
        self.start = timezone.now().replace(microsecond=0)

    def create_event(self, calendar, title, start):
        return CalendarEvent.objects.create(
            calendar=calendar, title=title, description='Bring your projects',
            start=start, end=start + timedelta(hours=1), location='Library',
        )

    def test_feed_contains_only_selected_calendar_events_in_descending_order(self):
        self.create_event(self.calendar, 'Earlier meeting', self.start)
        self.create_event(self.calendar, 'Later meeting', self.start + timedelta(days=1))
        other = Calendar.objects.create(name='Other', filename='other.ics')
        self.create_event(other, 'Private meeting', self.start)
        config = CalendarSettings.get_solo()
        config.vendor = 'Test School'
        config.product = 'Student Council'
        config.save()

        response = self.client.get(reverse('calendars_calendarfeed', args=[self.calendar.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertIn('text/calendar', response['Content-Type'])
        self.assertIn('school.ics', response['Content-Disposition'])
        feed = ICalendar.from_ical(response.content)
        self.assertEqual(str(feed['PRODID']), '-//Test School//Student Council//EN')
        events = feed.walk('VEVENT')
        self.assertEqual([str(event['SUMMARY']) for event in events], ['Later meeting', 'Earlier meeting'])
        self.assertEqual(events[1].decoded('DTSTART'), self.start)
        self.assertEqual(str(events[1]['DESCRIPTION']), 'Bring your projects')

    def test_empty_calendar_produces_valid_feed(self):
        response = self.client.get(reverse('calendars_calendarfeed', args=[self.calendar.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(ICalendar.from_ical(response.content).walk('VEVENT'), [])

    def test_missing_calendar_returns_404(self):
        response = self.client.get(reverse('calendars_calendarfeed', args=[self.calendar.pk + 1]))
        self.assertEqual(response.status_code, 404)

    def test_event_absolute_url_returns_event_details(self):
        event = self.create_event(self.calendar, 'Meeting', self.start)
        response = self.client.get(event.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['title'], 'Meeting')
        self.assertEqual(response.json()['calendar_id'], self.calendar.pk)
        self.assertEqual(response.json()['location'], 'Library')
