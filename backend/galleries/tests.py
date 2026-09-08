from io import BytesIO
from unittest.mock import patch
from django.forms import modelform_factory
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import SimpleTestCase
from PIL import Image
from .admin import PhotoAdminForm, VideoAdminForm
from .models import Photos, Videos

PhotoForm = modelform_factory(Photos, form=PhotoAdminForm, fields=['image'])
VideoForm = modelform_factory(Videos, form=VideoAdminForm, fields=['video_file'])
MP4 = bytes.fromhex('000000146674797069736f6d')


class GalleryUploadTests(SimpleTestCase):
    def test_optional_and_cleared_video(self):
        for data, expected in [({}, None), ({'video_file-clear': 'on'}, False)]:
            form = VideoForm(data=data)
            self.assertTrue(form.is_valid(), form.errors)
            self.assertIs(form.cleaned_data['video_file'], expected)

    def test_existing_files(self):
        for model, factory, field in [(Photos, PhotoForm, 'image'), (Videos, VideoForm, 'video_file')]:
            instance = model(**{field: 'existing.file'})
            with patch('galleries.admin.puremagic.from_string') as detect:
                form = factory(data={}, instance=instance)
                self.assertTrue(form.is_valid(), form.errors)
                self.assertIs(form.cleaned_data[field], getattr(instance, field))
                detect.assert_not_called()

    def test_video_types(self):
        for content in [MP4, bytes.fromhex('000000146674797071742020'), bytes.fromhex('1a45dfa3') + b'\0' * 20 + b'matroska']:
            upload = SimpleUploadedFile('video.bin', content)
            form = VideoForm(data={}, files={'video_file': upload})
            self.assertTrue(form.is_valid(), form.errors)
            self.assertEqual(upload.tell(), 0)

    def test_video_size_limit(self):
        for size, valid in [(4 * 1024 ** 3, True), (4 * 1024 ** 3 + 1, False)]:
            upload = SimpleUploadedFile('video.mp4', MP4)
            upload.size = size
            form = VideoForm(data={}, files={'video_file': upload})
            self.assertEqual(form.is_valid(), valid)
            if not valid:
                self.assertIn('max size is 4 GiB', str(form.errors))

    def test_unknown_and_disallowed_video(self):
        for content in [b'unknown upload', b'GIF89a' + b'\0' * 100]:
            upload = SimpleUploadedFile('video.mp4', content, content_type='video/mp4')
            form = VideoForm(data={}, files={'video_file': upload})
            self.assertFalse(form.is_valid())
            self.assertIn('video_file', form.errors)
            self.assertEqual(upload.tell(), 0)

    def photo(self, format='PNG', size=(100, 100)):
        stream = BytesIO()
        Image.new('RGB', size).save(stream, format=format)
        return SimpleUploadedFile('photo.' + format.lower(), stream.getvalue())

    def test_allowed_images(self):
        for format in ['JPEG', 'PNG', 'WEBP']:
            upload = self.photo(format)
            form = PhotoForm(data={}, files={'image': upload})
            self.assertTrue(form.is_valid(), form.errors)
            self.assertEqual(upload.tell(), 0)

    def test_image_dimensions(self):
        for size in [(99, 100), (100, 99), (4001, 100), (100, 4001)]:
            upload = self.photo(size=size)
            form = PhotoForm(data={}, files={'image': upload})
            self.assertFalse(form.is_valid())
            self.assertIn('dimensions', str(form.errors))
            self.assertEqual(upload.tell(), 0)

    def test_disallowed_image(self):
        form = PhotoForm(data={}, files={'image': self.photo('GIF')})
        self.assertFalse(form.is_valid())
        self.assertIn('Invalid file type', str(form.errors))

    def test_image_size_limit(self):
        upload = self.photo()
        upload.size = int(2.5 * 1024 * 1024) + 1
        form = PhotoForm(data={}, files={'image': upload})
        self.assertFalse(form.is_valid())
        self.assertIn('Max size is 2.5MB', str(form.errors))

    def test_corrupt_image(self):
        form = PhotoForm(data={}, files={'image': SimpleUploadedFile('photo.png', b'invalid')})
        self.assertFalse(form.is_valid())
        self.assertIn('image', form.errors)
