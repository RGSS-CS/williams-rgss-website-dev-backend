from io import BytesIO
from unittest.mock import patch
from django.forms import modelform_factory
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import SimpleTestCase, TestCase
from PIL import Image
from .admin import PhotoAdminForm
from .models import Photos
from clubs.models import Club
from management.admin import SiteSettingsAdminForm
from management.models import SiteSettings
from student_council.admin import STUCOAdminForm
from student_council.models import STUCO
from .serializers import PhotoSeralizer

PhotoForm = modelform_factory(Photos, form=PhotoAdminForm, fields=['image'])


class GalleryUploadTests(SimpleTestCase):
    def test_existing_files(self):
        for model, factory, field in [(Photos, PhotoForm, 'image')]:
            instance = model(**{field: 'existing.file'})
            with patch('galleries.validators.puremagic.from_string') as detect:
                form = factory(data={}, instance=instance)
                self.assertTrue(form.is_valid(), form.errors)
                self.assertIs(form.cleaned_data[field], getattr(instance, field))
                detect.assert_not_called()

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
        for size, valid in [
            ((99, 100), False), ((100, 99), False),
            ((100, 100), True),
            ((10000, 100), True), ((100, 10000), True),
            ((10001, 100), False), ((100, 10001), False),
        ]:
            with self.subTest(size=size):
                upload = self.photo(size=size)
                form = PhotoForm(data={}, files={'image': upload})
                self.assertEqual(form.is_valid(), valid, form.errors)
                if not valid:
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



class OtherImageUploadTests(SimpleTestCase):
    def test_admin_image_fields(self):
        for model, base_form, field, minimum in [
            (STUCO, STUCOAdminForm, 'stuco_logo', 100),
            (STUCO, STUCOAdminForm, 'group_photo', 100),
            (SiteSettings, SiteSettingsAdminForm, 'site_logo', 100),
            (SiteSettings, SiteSettingsAdminForm, 'favicon', 32),
        ]:
            # Keep the actual admin fields/cleaners without unrelated required fields.
            factory = modelform_factory(model, form=base_form, fields=[field])

            def form_for(data=None, files=None, instance=None):
                form = factory(data=data or {}, files=files, instance=instance)
                for name in list(form.fields):
                    if name != field:
                        del form.fields[name]
                return form

            with self.subTest(field=field):
                required = field in ('stuco_logo', 'favicon', 'site_logo')
                empty_form = form_for()
                self.assertEqual(empty_form.is_valid(), not required)
                if required:
                    self.assertEqual(empty_form.errors.as_data()[field][0].code, 'required')
                instance = model(**{field: 'existing.png'})
                with patch('galleries.validators.puremagic.from_string') as detect:
                    form = form_for(instance=instance)
                    self.assertTrue(form.is_valid(), form.errors)
                    detect.assert_not_called()
                form = form_for(data={field + '-clear': 'on'}, instance=instance)
                self.assertTrue(form.is_valid(), form.errors)
                if required:
                    self.assertEqual(form.cleaned_data[field], getattr(instance, field))
                else:
                    self.assertIs(form.cleaned_data[field], False)

            for format, size, oversized, valid in [
                ('PNG', (minimum, minimum), False, True),
                ('JPEG', (100, 100), False, True),
                ('WEBP', (100, 100), False, True),
                ('GIF', (100, 100), False, False),
                ('PNG', (minimum - 1, minimum), False, False),
                ('PNG', (10001, 100), False, False),
                ('PNG', (100, 100), True, False),
            ]:
                with self.subTest(field=field, format=format, size=size, oversized=oversized):
                    stream = BytesIO()
                    Image.new('RGB', size).save(stream, format=format)
                    upload = SimpleUploadedFile('image.' + format.lower(), stream.getvalue())
                    if oversized:
                        upload.size = int(2.5 * 1024 * 1024) + 1
                    form = form_for(files={field: upload})
                    self.assertEqual(form.is_valid(), valid, form.errors)
                    if not valid:
                        self.assertIn(field, form.errors)
                    self.assertEqual(upload.tell(), 0)

            form = form_for(files={field: SimpleUploadedFile('image.png', b'invalid')})
            self.assertFalse(form.is_valid())
            self.assertIn(field, form.errors)


@patch('requests.post')
class GalleryModelTests(TestCase):
    def test_named_media_and_visibility_updates_are_saved(self, request):
        club = Club.objects.create(name='Photography')
        for model, serializer, fields in (
            (Photos, PhotoSeralizer, {'image': 'existing/photo.png'}),
        ):
            with self.subTest(model=model):
                media = model.objects.create(club=club, name='Club day', **fields)
                self.assertIsNotNone(media.pk)
                media.refresh_from_db()
                self.assertFalse(media.shown_in_gallery)
                self.assertFalse(media.shown_in_main_page)
                media.shown_in_gallery = True
                media.shown_in_main_page = True
                media.save()
                media.refresh_from_db()
                data = serializer(media).data
                self.assertTrue(data['shown_in_gallery'])
                self.assertTrue(data['shown_in_main_page'])
                self.assertEqual(data['name'], 'Club day')

    def test_blank_names_are_generated_once(self, request):
        club = Club.objects.create(name='A club with a very long name')
        for model in (Photos,):
            for name in (None, '', '   '):
                with self.subTest(model=model, name=name):
                    media = model.objects.create(club=club, name=name)
                    self.assertIsNotNone(media.pk)
                    media.refresh_from_db()
                    generated = media.name
                    self.assertTrue(generated.startswith(club.name[:17] + ' - '))
                    media.description = 'Updated caption'
                    media.save()
                    media.refresh_from_db()
                    self.assertEqual(media.name, generated)
                    self.assertEqual(media.description, 'Updated caption')


class ImageUploadFilenameTests(SimpleTestCase):
    def test_all_image_fields_generate_unique_uuid4_filenames(self):
        from pathlib import Path
        from uuid import UUID

        for model, field_name, directory in [
            (Photos, 'image', 'clubs/None/photos'),
            (SiteSettings, 'favicon', 'upload/management'),
            (SiteSettings, 'site_logo', 'upload/management'),
            (STUCO, 'group_photo', 'upload/stuco'),
            (STUCO, 'stuco_logo', 'upload/stuco'),
        ]:
            with self.subTest(model=model.__name__, field=field_name):
                field = model._meta.get_field(field_name)
                instance = model()
                names = [field.generate_filename(instance, 'Original Photo.PNG') for _ in range(2)]
                self.assertNotEqual(*names)
                for name in names:
                    path = Path(name)
                    self.assertEqual(path.parent.as_posix(), directory)
                    self.assertEqual(path.suffix, '.png')
                    self.assertEqual(UUID(hex=path.stem).version, 4)
                    self.assertEqual(UUID(hex=path.stem).hex, path.stem)
