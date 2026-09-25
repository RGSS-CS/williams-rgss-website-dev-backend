from io import BytesIO, StringIO
from unittest.mock import patch

from django.core.management import call_command
from django.core.management.base import CommandError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import SimpleTestCase, TestCase, override_settings
from PIL import Image

from .apps import CommandsConfig

from clubs.models import Club, ClubAnnouncement
from management.models import PageSettings, SchoolSocialMedia, SiteSettings
from student_council.models import Announcements, SchoolAnnouncements, STUCO


class GenerateTestDataTests(TestCase):
    def setUp(self):
        # Saves trigger frontend revalidation; never contact a running frontend.
        request = patch('requests.post')
        request.start()
        self.addCleanup(request.stop)

    def generate(self, **options):
        output = StringIO()
        call_command('generate_testdata', stdout=output, **options)
        return output.getvalue()

    def test_generates_valid_clubs_and_related_content(self):
        self.generate(seed='regression', club_amount=10)
        self.assertEqual(Club.objects.count(), 10)
        for club in Club.objects.all():
            club.full_clean()
            self.assertTrue(club.location.startswith('Room '))
            self.assertTrue(club.category.exists())
            announcement = club.club_announcement.get()
            announcement.full_clean()
            self.assertGreater(announcement.expiry, announcement.date_posted)

    @override_settings(STORAGES={
        'default': {'BACKEND': 'django.core.files.storage.InMemoryStorage'},
    })
    def test_seeds_current_settings_models_without_duplicates(self):
        def image():
            stream = BytesIO()
            Image.new('RGB', (160, 160)).save(stream, format='PNG')
            return SimpleUploadedFile('existing.png', stream.getvalue(), content_type='image/png')

        settings = SiteSettings.get_solo()
        settings.frontend_url = 'https://frontend.example.com'
        settings.captcha = ['LOGIN']
        settings.favicon = image()
        settings.site_logo = image()
        settings.save()
        favicon, site_logo = settings.favicon.name, settings.site_logo.name
        council = STUCO.get_solo()
        council.stuco_logo = image()
        council.group_photo = image()
        council.save()
        stuco_logo, group_photo = council.stuco_logo.name, council.group_photo.name
        for _ in range(2):
            self.generate(seed='settings', skip_clubs=True)
        settings.refresh_from_db()
        self.assertEqual(settings.school_domain, 'example.com')
        self.assertEqual(settings.frontend_url, 'https://frontend.example.com')
        self.assertEqual(settings.captcha, ['LOGIN'])
        self.assertEqual(settings.favicon.name, favicon)
        self.assertEqual(settings.site_logo.name, site_logo)
        settings.full_clean()
        self.assertEqual(SiteSettings.objects.count(), 1)
        self.assertEqual(STUCO.objects.count(), 1)
        council = STUCO.get_solo()
        self.assertTrue(council.council_name)
        self.assertTrue(council.photo_caption)
        self.assertEqual(council.stuco_logo.name, stuco_logo)
        self.assertEqual(council.group_photo.name, group_photo)
        council.full_clean()
        self.assertEqual(len(Announcements.get_solo().ticker_items.splitlines()), 3)
        self.assertEqual(SchoolAnnouncements.objects.count(), 3)
        self.assertEqual(PageSettings.objects.count(), len(PageSettings.PageTypes))
        self.assertEqual(SchoolSocialMedia.objects.count(), len(SchoolSocialMedia.Sites))
        for model in (PageSettings, SchoolSocialMedia, Announcements, SchoolAnnouncements):
            for obj in model.objects.all():
                obj.full_clean()

    def test_skip_settings_leaves_settings_untouched(self):
        self.generate(seed='clubs-only', club_amount=1, skip_settings=True)
        self.assertEqual(Club.objects.count(), 1)
        self.assertFalse(SiteSettings.objects.exists())
        self.assertFalse(STUCO.objects.exists())
        self.assertFalse(Announcements.objects.exists())
        self.assertFalse(SchoolAnnouncements.objects.exists())
        self.assertFalse(SchoolSocialMedia.objects.exists())

    def test_skip_clubs_and_zero_amount_create_no_club_content(self):
        for options in ({'skip_clubs': True}, {'club_amount': 0}):
            with self.subTest(options=options):
                self.generate(skip_settings=True, **options)
                self.assertFalse(Club.objects.exists())
                self.assertFalse(ClubAnnouncement.objects.exists())

    def test_negative_amount_fails_before_writing(self):
        with self.assertRaisesMessage(CommandError, '--club-amount must be non-negative'):
            self.generate(club_amount=-1)
        self.assertFalse(SiteSettings.objects.exists())

    def test_seed_reproduces_club_fields_and_tags(self):
        self.generate(seed='repeatable', club_amount=2, skip_settings=True)
        first = list(Club.objects.order_by('name').values('name', 'location', 'description', 'tagline'))
        tags = [list(club.category.values_list('name', flat=True)) for club in Club.objects.order_by('name')]
        Club.objects.all().delete()
        self.generate(seed='repeatable', club_amount=2, skip_settings=True)
        self.assertEqual(first, list(Club.objects.order_by('name').values('name', 'location', 'description', 'tagline')))
        self.assertEqual(tags, [list(club.category.values_list('name', flat=True)) for club in Club.objects.order_by('name')])

    def test_school_announcements_have_content_and_reproducible_values(self):
        self.generate(seed='school-news', skip_clubs=True)
        first = list(SchoolAnnouncements.objects.order_by('title').values('title', 'contents'))
        self.assertEqual(len(first), 3)
        for announcement in SchoolAnnouncements.objects.all():
            self.assertTrue(announcement.title)
            self.assertTrue(announcement.contents)
            self.assertIsNotNone(announcement.date_posted)
            self.assertIsNotNone(announcement.date_modified)
        SchoolAnnouncements.objects.all().delete()
        self.generate(seed='school-news', skip_clubs=True)
        self.assertEqual(first, list(SchoolAnnouncements.objects.order_by('title').values('title', 'contents')))

    def test_failure_rolls_back_seeded_data(self):
        with patch('commands.management.commands.generate_testdata.ClubAnnouncement.objects.create', side_effect=RuntimeError('failed')):
            with self.assertRaisesMessage(RuntimeError, 'failed'):
                self.generate(club_amount=1)
        self.assertFalse(Club.objects.exists())
        self.assertFalse(SchoolAnnouncements.objects.exists())
        self.assertFalse(STUCO.objects.exists())
        self.assertFalse(SiteSettings.objects.exists())


class CommandsConfigTests(SimpleTestCase):
    def test_app_name_is_commands(self):
        self.assertEqual(CommandsConfig.name, "commands")
