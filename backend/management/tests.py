from django.test import TestCase
from django.urls import reverse

from .models import PageSettings, SchoolSocialMedia, SiteSettings


class ManagementModelTests(TestCase):
    def test_site_settings_have_expected_defaults(self):
        site_settings = SiteSettings.get_solo()

        self.assertFalse(site_settings.maintainance_mode)
        self.assertEqual(site_settings.school_name, "SCHOOL")
        self.assertFalse(site_settings.favicon)
        self.assertFalse(site_settings.site_logo)
        self.assertEqual(str(site_settings), "Site Configuration")

    def test_page_settings_use_display_name_for_string_representation(self):
        page_settings = PageSettings.objects.create(
            internal_site_name=PageSettings.PageTypes.HOME,
            title="Welcome"
        )

        self.assertEqual(str(page_settings), "Home")


class SchoolSocialMediaTests(TestCase):
    def setUp(self):
        self.site_settings = SiteSettings.get_solo()

    def test_social_media_is_available_through_site_settings(self):
        instagram = SchoolSocialMedia.objects.create(
            site_settings=self.site_settings,
            social_type=SchoolSocialMedia.Sites.INSTAGRAM,
            title="Student Council Instagram",
            link="https://www.instagram.com/example_school/",
        )

        self.assertEqual(list(self.site_settings.social_media.all()), [instagram])
        self.assertEqual(str(instagram), "IG")

    def test_social_media_string_representation_handles_optional_title(self):
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

    def test_site_settings_endpoint_returns_social_media_details(self):
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
