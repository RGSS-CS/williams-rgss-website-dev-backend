from pathlib import Path
from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse

from .apps import ManagementConfig
from .legalDefaults import privacyPolicy, termsService
from .models import Legal, PageSettings, SchoolSocialMedia, SiteSettings
from .signals import on_management_change


class ManagementModelTests(TestCase):
    def test_site_defaults(self):
        site_settings = SiteSettings.get_solo()

        self.assertTrue(site_settings.maintainance_mode)
        self.assertEqual(site_settings.school_name, "SCHOOL")
        self.assertFalse(site_settings.favicon)
        self.assertFalse(site_settings.site_logo)
        self.assertEqual(str(site_settings), "Site Configuration")

    def test_page_display(self):
        page_settings = PageSettings.objects.create(
            internal_site_name=PageSettings.PageTypes.HOME,
            title="Welcome"
        )

        self.assertEqual(str(page_settings), "Home")


class LegalDefaultsTests(TestCase):
    def test_legal_static(self):
        self.assertEqual(
            termsService(),
            (Path(__file__).parent / "legal_defaults" / "terms_service.md")
            .read_text(encoding="utf-8"),
        )
        self.assertEqual(
            privacyPolicy(),
            (Path(__file__).parent / "legal_defaults" / "privacy_policy.md")
            .read_text(encoding="utf-8"),
        )

    def test_legal_markdown(self):
        legal = Legal()

        self.assertEqual(legal.terms_service, termsService())
        self.assertEqual(legal.privacy_policy, privacyPolicy())


class ManagementSignalTests(TestCase):
    @patch("management.signals.revalidate_frontend_tag")
    def test_migrate_signal(self, revalidate):
        on_management_change(sender=SiteSettings, app_config=None)

        revalidate.assert_called_once_with("management")


class SchoolSocialMediaTests(TestCase):
    def setUp(self):
        self.site_settings = SiteSettings.get_solo()

    def test_social_settings(self):
        instagram = SchoolSocialMedia.objects.create(
            site_settings=self.site_settings,
            social_type=SchoolSocialMedia.Sites.INSTAGRAM,
            title="Student Council Instagram",
            link="https://www.instagram.com/example_school/",
        )

        self.assertEqual(list(self.site_settings.social_media.all()), [instagram])
        self.assertEqual(str(instagram), "IG")

    def test_optional_title(self):
        for title in ("", None):
            with self.subTest(title=title):
                instagram = SchoolSocialMedia.objects.create(
                    site_settings=self.site_settings,
                    social_type=SchoolSocialMedia.Sites.INSTAGRAM,
                    title=title,
                    link="https://www.instagram.com/example_school/",
                )

                instagram.refresh_from_db()
                self.assertEqual(str(instagram), "IG")

    def test_settings_api(self):
        SchoolSocialMedia.objects.create(
            site_settings=self.site_settings,
            social_type=SchoolSocialMedia.Sites.INSTAGRAM,
            title="Instagram",
            link="https://www.instagram.com/example_school/",
        )
        SchoolSocialMedia.objects.create(
            site_settings=self.site_settings,
            social_type=SchoolSocialMedia.Sites.YOUTUBE,
            title="YouTube",
            link="https://www.youtube.com/@example_school",
        )

        response = self.client.get(reverse("site-settings-list"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json()[0]["social_media"],
            [
                {
                    "social_type": SchoolSocialMedia.Sites.INSTAGRAM,
                    "title": "Instagram",
                    "link": "https://www.instagram.com/example_school/",
                },
                {
                    "social_type": SchoolSocialMedia.Sites.YOUTUBE,
                    "title": "YouTube",
                    "link": "https://www.youtube.com/@example_school",
                },
            ],
        )
