from django.conf import settings
from django.test import SimpleTestCase


class MarkdownXRouteConfigTests(SimpleTestCase):
    def test_markdownx_preview_routes_use_api_prefix(self):
        self.assertEqual(settings.MARKDOWNX_URLS_PATH, "/api/markdownx/markdownify/")
        self.assertEqual(settings.MARKDOWNX_UPLOAD_URLS_PATH, "/api/markdownx/upload/")
