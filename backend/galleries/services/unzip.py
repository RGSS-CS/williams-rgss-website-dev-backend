from io import BytesIO
from pathlib import PurePosixPath
from zipfile import BadZipFile, ZipFile

from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import transaction

from galleries.models import Photos
from galleries.validators import validate_image_upload

MAX_FILES = 100
MAX_UNCOMPRESSED_BYTES = 100 * 1024 * 1024 # 100MiB
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}


def import_zip_photos(mass_import):
    try:
        with ZipFile(mass_import.zip_file) as archive:
            entries = [
                entry for entry in archive.infolist()
                if not entry.is_dir()
                and not entry.filename.startswith("__MACOSX/")
                and PurePosixPath(entry.filename).name != ".DS_Store"
            ]

            if not entries:
                raise ValidationError("The ZIP file does not contain any files.")

            if len(entries) > MAX_FILES:
                raise ValidationError(f"A ZIP can contain at most {MAX_FILES} photos.")

            if sum(entry.file_size for entry in entries) > MAX_UNCOMPRESSED_BYTES:
                raise ValidationError("The ZIP contents are too large.")

            uploads = []
            for entry in entries:
                path = PurePosixPath(entry.filename)

                if path.is_absolute() or ".." in path.parts:
                    raise ValidationError("The ZIP contains an unsafe file path.")

                if entry.flag_bits & 0x1:
                    raise ValidationError("Password-protected ZIP files are not supported.")

                if path.suffix.lower() not in ALLOWED_EXTENSIONS:
                    raise ValidationError(f"{path.name} is not a supported image type.")

                content = archive.read(entry)
                upload = SimpleUploadedFile(
                    path.name,
                    content,
                    content_type=None,
                )
                validate_image_upload(upload)
                uploads.append(upload)

    except BadZipFile as exc:
        raise ValidationError("Upload a valid ZIP file.") from exc

    with transaction.atomic():
        for upload in uploads:
            Photos.objects.create(
                club=mass_import.club,
                image=upload,
            )