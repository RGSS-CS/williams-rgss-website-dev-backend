from django.contrib.admin.widgets import AdminFileWidget
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import SimpleTestCase

from .admin import VideoAdmin, VideoAdminForm


class VideoAdminFormTests(SimpleTestCase):
    def setUp(self):
        self.field = VideoAdminForm.base_fields['video_file']

    def test_admin_uses_form_and_admin_widget(self):
        self.assertIs(VideoAdmin.form, VideoAdminForm)
        self.assertIsInstance(self.field.widget, AdminFileWidget)

    def test_upload_is_optional_and_can_be_cleared(self):
        self.assertIsNone(self.field.clean(None))
        self.assertIs(self.field.clean(False), False)

    def test_existing_file_is_preserved_without_replacement(self):
        existing = SimpleUploadedFile('existing.mp4', b'video')
        self.assertIs(self.field.clean(None, initial=existing), existing)

    def test_size_limit(self):
        for size in (2000 * 1024 ** 2, 2 * 1024 ** 3):
            with self.subTest(size=size):
                upload = SimpleUploadedFile('video.mp4', b'video')
                upload.size = size
                self.assertIs(self.field.clean(upload), upload)

        upload.size += 1
        with self.assertRaisesMessage(ValidationError, 'The max size is 2 GiB.'):
            self.field.clean(upload)
