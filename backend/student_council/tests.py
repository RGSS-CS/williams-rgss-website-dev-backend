from datetime import timedelta
from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Announcements, SchoolAnnouncements, STUCO


class StudentCouncilTests(TestCase):
    def setUp(self):
        request = patch('requests.post')
        request.start()
        self.addCleanup(request.stop)

    def test_council_defaults_and_singleton(self):
        council = STUCO.get_solo()
        self.assertEqual(council.council_name, 'STUCO')
        self.assertFalse(council.group_photo)
        self.assertIsNone(council.photo_caption)
        self.assertEqual(STUCO.get_solo().pk, council.pk)

    def test_council_endpoint_includes_photo_caption(self):
        council = STUCO.get_solo()
        council.council_name = 'SAC'
        council.photo_caption = 'Your student council'
        council.save()
        response = self.client.get(reverse('stuco-settings-list'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()[0], {
            'council_name': 'SAC', 'group_photo': None,
            'photo_caption': 'Your student council',
        })

    def test_announcements_preserve_newlines_and_allow_empty_ticker(self):
        announcements = Announcements.get_solo()
        for ticker in ('Welcome!\nClub fair on Friday', '', None):
            with self.subTest(ticker=ticker):
                announcements.ticker_items = ticker
                announcements.full_clean()
                announcements.save()
                response = self.client.get(reverse('announcements-list'))
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.json(), [{'ticker_items': ticker}])
        self.assertEqual(Announcements.objects.count(), 1)


class SchoolAnnouncementTests(TestCase):
    def test_multiple_announcements_preserve_title_and_contents(self):
        for title, contents in (
            ('Club fair', 'Meet our clubs.\nFriday in the gym.'),
            ('Spirit week', 'Wear school colours on Monday.'),
        ):
            announcement = SchoolAnnouncements.objects.create(title=title, contents=contents)
            announcement.full_clean()
            announcement.refresh_from_db()
            self.assertEqual(str(announcement), title)
            self.assertEqual(announcement.contents, contents)
        self.assertEqual(SchoolAnnouncements.objects.count(), 2)

    def test_edit_updates_modified_date_and_preserves_posted_date(self):
        posted = timezone.now() - timedelta(days=1)
        modified = posted + timedelta(hours=2)
        with patch('django.utils.timezone.now', return_value=posted):
            announcement = SchoolAnnouncements.objects.create(title='Club fair', contents='Friday')
        self.assertEqual(announcement.date_posted, posted)
        self.assertEqual(announcement.date_modified, posted)
        with patch('django.utils.timezone.now', return_value=modified):
            announcement.contents = 'Moved to Monday'
            announcement.save()
        announcement.refresh_from_db()
        self.assertEqual(announcement.contents, 'Moved to Monday')
        self.assertEqual(announcement.date_posted, posted)
        self.assertEqual(announcement.date_modified, modified)
