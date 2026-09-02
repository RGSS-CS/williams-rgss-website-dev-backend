from django.test import TestCase

from .models import PageSettings, SiteSettings


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
