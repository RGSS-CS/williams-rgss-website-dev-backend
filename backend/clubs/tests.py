from datetime import timedelta
from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Club, ClubAnnouncement
from .serializers import ClubSerializer, PublicClubSerializer


class ClubSerializerTests(TestCase):
    def setUp(self):
        revalidation = patch('requests.post')
        revalidation.start()
        self.addCleanup(revalidation.stop)

    def test_serializer_returns_expected_club_fields(self):
        club = Club.objects.create(
            name="Coding Club",
            preview_description="A club for builders",
            description="A place to explore software",
            tagline="Build together",
            repetition=Club.Repetition.WEEKLY,
            day_of_meeting=Club.WeekDay.MONDAY,
        )

        serializer = ClubSerializer(club)
        data = serializer.data

        self.assertEqual(data["name"], "Coding Club")
        self.assertEqual(data["tagline"], "Build together")
        self.assertEqual(data["day_of_meeting"], Club.WeekDay.MONDAY)
        self.assertIn("category", data)


@patch('requests.post')
class CurrentClubFieldsTests(TestCase):
    def test_location_supports_room_names_and_is_serialized(self, request):
        for location in ('Room 201', 'Library', '', None):
            with self.subTest(location=location):
                club = Club.objects.create(name=f'Club {location}', location=location)
                club.refresh_from_db()
                for serializer in (ClubSerializer, PublicClubSerializer):
                    data = serializer(club).data
                    self.assertEqual(data['location'], location)
                    self.assertNotIn('room_number', data)

    def test_announcement_fields_and_related_content(self, request):
        club = Club.objects.create(name='Robotics')
        now = timezone.now()
        announcement = ClubAnnouncement.objects.create(
            club=club, title='Build day', description='Bring your projects',
            expiry=now + timedelta(days=1), popup=True,
        )
        announcement.refresh_from_db()
        self.assertGreaterEqual(announcement.date_posted, now)
        self.assertEqual(str(announcement), 'Build day')
        data = ClubSerializer(club).data['announcement'][0]
        self.assertEqual(data['title'], 'Build day')
        self.assertTrue(data['popup'])
        self.assertIn('expiry', data)
        self.assertNotIn('pinned', data)
        club.delete()
        self.assertFalse(ClubAnnouncement.objects.filter(pk=announcement.pk).exists())

    def test_club_endpoints_return_empty_announcement_lists(self, request):
        club = Club.objects.create(name='Chess')
        detail = self.client.get(reverse('club-detail', args=[club.pk]))
        listing = self.client.get(reverse('club-list'))
        self.assertEqual(detail.status_code, 200)
        self.assertEqual(listing.status_code, 200)
        self.assertEqual(detail.json()['announcement'], [])
        self.assertEqual(listing.json()[0]['announcement'], [])

    def test_club_endpoints_include_multiple_related_announcements(self, request):
        club = Club.objects.create(name='Robotics')
        other = Club.objects.create(name='Chess')
        now = timezone.now()
        for title, popup, expiry in (
            ('Build day', True, now + timedelta(days=1)),
            ('Previous meeting', False, now - timedelta(days=1)),
        ):
            ClubAnnouncement.objects.create(
                club=club, title=title, description='Bring your projects',
                date_posted=now, popup=popup, expiry=expiry,
            )
        ClubAnnouncement.objects.create(club=other, title='Chess only')

        detail = self.client.get(reverse('club-detail', args=[club.pk]))
        listing = self.client.get(reverse('club-list'))
        self.assertEqual(detail.status_code, 200)
        self.assertEqual(listing.status_code, 200)
        listed_club = next(item for item in listing.json() if item['id'] == club.pk)
        for data in (detail.json(), listed_club):
            with self.subTest(data=data):
                announcements = {item['title']: item for item in data['announcement']}
                self.assertEqual(set(announcements), {'Build day', 'Previous meeting'})
                self.assertTrue(announcements['Build day']['popup'])
                self.assertFalse(announcements['Previous meeting']['popup'])
                for item in announcements.values():
                    self.assertEqual(set(item), {
                        'title', 'description', 'date_posted', 'popup', 'expiry',
                    })
                    self.assertEqual(item['description'], 'Bring your projects')
                    self.assertIsNotNone(item['expiry'])
                    self.assertIsNotNone(item['date_posted'])
