"""
seed_dev_data.py

Seeds a dev instance of the RGSS Williams Portal backend with:
  1. Clubs — every field on the Club model (clubs/models.py) is randomized,
     including the choice fields (WeekDay, Repetition, AcceptingApplications),
     and each club gets a real Photologue Gallery with a randomized number of
     randomly generated photos attached (fills the `# TODO: add image` from
     the pre-existing `generate_testdata.py` in this same app).
  2. SiteSettings (the singleton config row) — every field is randomized too.
     Done directly via the ORM because `SiteSettingsViewSet` in
     management/views.py is a `ReadOnlyModelViewSet` (see management/urls.py),
     so there is no POST/PATCH endpoint to hit over HTTP — the ORM/management
     command route is the only way to seed it programmatically.

WHY A MANAGEMENT COMMAND INSTEAD OF AN HTTP SCRIPT FOR EVERYTHING:
  - Club creation IS exposed at POST /api/club/ (clubs/views.py -> ClubViewSet
    is a full ModelViewSet), and image upload IS exposed at
    POST /api/photologue/clubs/<id>/gallery/ and
    POST /api/photologue/clubs/<id>/gallery/photos/ (photologue_custom/views.py,
    on the `feature/img-upload` branch). Those two alone *could* be driven by
    an HTTP script against a running dev server.
  - But SiteSettings has no write endpoint at all, so a pure-HTTP script can't
    finish the job. Running everything as one `manage.py` command against the
    dev DB directly (same DB the dev server reads from) avoids needing two
    different tools/auth paths for one seeding pass.

IMAGES:
  Photologue's `Photo.save()` runs Pillow processing (thumbnail/display-size
  generation) on save, so it needs real, decodable image bytes — an empty or
  fake file raises `UnidentifiedImageError`. Each generated image here is a
  genuinely random PNG: random size, random background color, and a handful
  of random colored shapes (rectangles/ellipses/lines) drawn with
  `PIL.ImageDraw`, so galleries don't end up with visually-identical flat
  color swatches.

USAGE (on the dev server / dev container, same repo the API is running from):
    python manage.py seed_dev_data
    python manage.py seed_dev_data --seed 12345 --club-amount 10
    python manage.py seed_dev_data --skip-settings   # only clubs/images
    python manage.py seed_dev_data --skip-clubs       # only SiteSettings

Place this file at:
    backend/commands/management/commands/seed_dev_data.py
(same app as the existing generate_testdata.py command.)
"""

import datetime
import io
import random
import string
import uuid

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from PIL import Image, ImageDraw

from clubs.models import Club
from management.models import SiteSettings
from photologue.models import Gallery, Photo


def random_string(length: int) -> str:
    return "".join(random.choices(string.ascii_letters + string.digits, k=length))


def random_bool() -> bool:
    return random.choice([True, False])


def random_hex_color() -> str:
    return "#{:06X}".format(random.randint(0, 0xFFFFFF))


def random_sentence(word_count_range=(4, 12)) -> str:
    words = [random_string(random.randint(3, 9)) for _ in range(random.randint(*word_count_range))]
    return " ".join(words) + "."


def random_email() -> str:
    return f"{random_string(8).lower()}@example.com"


def random_phone() -> str:
    # E.164-ish Canadian-looking number; PhoneNumberField(region="CA") just
    # needs something parseable, not a real line.
    return "+1416" + "".join(random.choices(string.digits, k=7))


def random_url() -> str:
    return f"https://{random_string(10).lower()}.example.com/{random_string(6).lower()}"


def random_time() -> datetime.time:
    return datetime.time(random.randint(0, 23), random.randint(0, 59))


# ---------------------------------------------------------------------------
# Randomized image generation
# ---------------------------------------------------------------------------

def make_random_image_bytes() -> bytes:
    """
    Builds one genuinely random PNG: random dimensions, random background
    color, and 1-6 random shapes in random colors/positions. Returned as raw
    bytes ready for ContentFile.
    """
    width = random.randint(200, 800)
    height = random.randint(200, 800)
    bg_color = tuple(random.randint(0, 255) for _ in range(3))

    image = Image.new("RGB", (width, height), bg_color)
    draw = ImageDraw.Draw(image)

    for _ in range(random.randint(1, 6)):
        shape_color = tuple(random.randint(0, 255) for _ in range(3))
        x0, x1 = sorted([random.randint(0, width), random.randint(0, width)])
        y0, y1 = sorted([random.randint(0, height), random.randint(0, height)])
        shape_type = random.choice(["rectangle", "ellipse", "line"])
        if shape_type == "rectangle":
            draw.rectangle([x0, y0, x1, y1], fill=shape_color)
        elif shape_type == "ellipse":
            draw.ellipse([x0, y0, x1, y1], fill=shape_color)
        else:
            draw.line([x0, y0, x1, y1], fill=shape_color, width=random.randint(1, 12))

    buf = io.BytesIO()
    image.save(buf, "PNG")
    buf.seek(0)
    return buf.read()


def make_random_photo(name_hint: str) -> Photo:
    """
    Creates a Photologue Photo the same way PhotoUploadSerializer.create()
    does in photologue_custom/serializers.py: title falls back to filename,
    slug is title + a short uuid suffix so it doesn't collide (Photo.slug is
    unique=True in photologue/models.py).
    """
    filename = f"{name_hint}-{uuid.uuid4().hex[:8]}.png"
    photo = Photo(
        title=random_string(20),
        slug=filename.rsplit(".", 1)[0],
        caption=random_sentence((2, 8)),
        is_public=random_bool(),
    )
    photo.image.save(filename, ContentFile(make_random_image_bytes()), save=False)
    photo.save()
    return photo


def make_random_gallery(club_name: str) -> Gallery:
    photo_count = random.randint(1, 8)
    gallery = Gallery.objects.create(
        title=f"{club_name} Gallery",
        slug=f"{club_name[:40]}-gallery-{uuid.uuid4().hex[:8]}".lower().replace(" ", "-"),
        description=random_sentence((5, 15)),
        is_public=random_bool(),
    )
    for i in range(photo_count):
        photo = make_random_photo(f"{club_name}-{i}")
        gallery.photos.add(photo)
    return gallery


class Command(BaseCommand):
    help = """
    Seeds dev data: Clubs (every field randomized, each with a real
    Photologue gallery of randomly generated photos) and SiteSettings (every
    field randomized). Run this directly against the dev server/DB, e.g.:

        python manage.py seed_dev_data

    Options:
        -s --seed         RNG seed (default: random)
        -c --club-amount  number of Clubs to create (default: 10)
        --skip-clubs      don't create clubs/images
        --skip-settings   don't touch SiteSettings
    """

    def add_arguments(self, parser):
        parser.add_argument("-s", "--seed", default=None)
        parser.add_argument("-c", "--club-amount", type=int, default=10)
        parser.add_argument("--skip-clubs", action="store_true")
        parser.add_argument("--skip-settings", action="store_true")

    def handle(self, *args, **options):
        seed = options["seed"] or random.randint(10**16, 10**17 - 1)
        random.seed(seed)

        if not options["skip_settings"]:
            self.seed_site_settings()

        if not options["skip_clubs"]:
            self.seed_clubs(club_amount=options["club_amount"])

        self.stdout.write(self.style.SUCCESS(f"Done seeding dev data (seed={seed})."))

    def seed_site_settings(self):
        """
        SiteSettings is a django-solo SingletonModel (management/models.py),
        so get_solo() always returns the single row, creating it with field
        defaults on first call if it doesn't exist yet. Every non-image,
        non-relation field is randomized.
        """
        settings_obj = SiteSettings.get_solo()
        settings_obj.maintainance_mode = random_bool()
        settings_obj.school_name = random_string(20)
        settings_obj.council_name = random_string(8)
        settings_obj.school_email = random_email()
        settings_obj.school_phone = random_phone()
        settings_obj.about_stuco = random_sentence((15, 40))
        settings_obj.about_school = random_sentence((15, 40))
        settings_obj.school_mascot = random_string(10)
        settings_obj.school_primary_color = random_hex_color()
        settings_obj.school_secondary_color = random_hex_color()
        settings_obj.school_tertiary_color = random_hex_color()
        settings_obj.save()
        self.stdout.write(f"SiteSettings seeded (pk={settings_obj.pk}).")

    def seed_clubs(self, club_amount: int):
        # NOTE: the pre-existing `generate_testdata.py` in this same app passes
        # `motto=...` to Club.objects.create(), but `Club` (clubs/models.py on
        # this branch) has no `motto` field — that command currently raises
        # TypeError if run. Not reproduced here; only real Club fields are set.
        weekdays = [c[0] for c in Club.WeekDay.choices]
        repetitions = [c[0] for c in Club.Repetition.choices]
        accepting_choices = [c[0] for c in Club.AcceptingApplications.choices]

        for _ in range(club_amount):
            name = f"{random_string(8)} Club"
            club = Club.objects.create(
                name=name,
                preview_description=random_sentence((10, 25)),
                description=random_sentence((30, 70)),
                repetition=random.choice(repetitions),
                classroom_code=random_string(7),
                accepting_applicants=random.choice(accepting_choices),
                application_form_link=random_url(),
                announcement=random_sentence((5, 15)),
                day_of_meeting=random.choice(weekdays),
                time=random_time(),
                room_number=random.randint(100, 499),
                teacher_advisor="Mr./Mrs./Ms. " + random_string(8),
                tagline=random_sentence((3, 8)),
                join_instructions=random_sentence((10, 25)),
            )

            for _ in range(random.randint(1, 5)):
                club.category.add(random_string(10))

            # Fills the `# TODO: add image` from the original generate_testdata.py
            club.gallery = make_random_gallery(name)
            club.save(update_fields=["gallery"])

            self.stdout.write(
                f"  created club '{club.name}' (id={club.id}) "
                f"with gallery id={club.gallery_id} "
                f"({club.gallery.photos.count()} photos)"
            )