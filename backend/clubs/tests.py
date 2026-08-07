from django.test import TestCase

from .models import Club, ClubWhyJoin
from .serializers import ClubSerializer


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
