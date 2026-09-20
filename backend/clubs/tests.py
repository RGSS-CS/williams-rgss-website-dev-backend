from datetime import timedelta
from unittest.mock import patch

from django.utils import timezone

from .models import Club, ClubAnnouncement, ClubWhyJoin
from .serializers import ClubSerializer, PublicClubSerializer


from django.test import TestCase



class ClubWhyJoinModelTests(TestCase):
    @patch('requests.post')
    def test_club_api_returns_reasons_in_saved_order(self, request):
        from rest_framework.test import APIRequestFactory
        from .views import ClubViewSet

        club = Club.objects.create(name="Ordered Club")
        first = ClubWhyJoin.objects.create(
            club=club, title="First", description="First reason", index=2,
        )
        second = ClubWhyJoin.objects.create(
            club=club, title="Second", description="Second reason", index=0,
        )
        third = ClubWhyJoin.objects.create(
            club=club, title="Third", description="Third reason", index=0,
        )
        view = ClubViewSet.as_view({'get': 'retrieve'})
        factory = APIRequestFactory()

        response = view(factory.get('/api/club/'), pk=club.pk)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            [item['id'] for item in response.data['why_join']],
            [second.pk, third.pk, first.pk],
        )

        first.index = 0
        second.index = 1
        third.index = 2
        ClubWhyJoin.objects.bulk_update([first, second, third], ['index'])

        response = view(factory.get('/api/club/'), pk=club.pk)

        self.assertEqual(
            [(item['id'], item['index']) for item in response.data['why_join']],
            [(first.pk, 0), (second.pk, 1), (third.pk, 2)],
        )

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
