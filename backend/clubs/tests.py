from datetime import timedelta
from unittest.mock import patch

from django.utils import timezone

from .models import Club, ClubAnnouncement, ClubChanges, ClubWhyJoin
from .serializers import ClubSerializer, PublicClubSerializer


from django.test import TestCase



class ClubWhyJoinModelTests(TestCase):
    def test_why_join_reasons_are_ordered_by_index(self):
        club = Club.objects.create(name="Science Club")
        ClubWhyJoin.objects.create(club=club, title="First reason", description="Desc 1", index=2)
        ClubWhyJoin.objects.create(club=club, title="Second reason", description="Desc 2", index=1)

        reasons = list(ClubWhyJoin.objects.filter(club=club))

        self.assertEqual([reason.title for reason in reasons], ["Second reason", "First reason"])


class ClubSerializerTests(TestCase):
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

    def test_approved_location_change_is_persisted(self, request):
        club = Club.objects.create(name='Chess', location='Room 101')
        change = ClubChanges.objects.create(club=club, changes={'location': 'Library'})
        change.approve(reviewer=None)
        club.refresh_from_db()
        self.assertEqual(club.location, 'Library')
        change.refresh_from_db()
        self.assertEqual(change.status, ClubChanges.ApprovalStatus.APPROVED)

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
