"""Seed randomized development clubs and site settings."""

import datetime
import random
import string

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from clubs.models import Club, ClubAnnouncement
from management.models import PageSettings, SchoolSocialMedia, SiteSettings
from student_council.models import Announcements, SchoolAnnouncements, STUCO


def random_string(length: int) -> str:
    return "".join(random.choices(string.ascii_letters + string.digits, k=length))


def random_bool() -> bool:
    return random.choice([True, False])


def random_sentence(word_count_range=(4, 12), max_length=None) -> str:
    words = [random_string(random.randint(3, 9)) for _ in range(random.randint(*word_count_range))]
    sentence = " ".join(words) + "."
    return sentence if max_length is None else sentence[:max_length]


def random_email() -> str:
    return f"{random_string(8).lower()}@example.com"


def random_phone() -> str:
    # Use a valid Canadian number in the fictional 555-01xx range.
    return "+141655501" + "".join(random.choices(string.digits, k=2))


def random_url() -> str:
    return f"https://{random_string(10).lower()}.example.com/{random_string(6).lower()}"


def random_time() -> datetime.time:
    return datetime.time(random.randint(0, 23), random.randint(0, 59))


class Command(BaseCommand):
    help = "Seed randomized development clubs and site settings."

    def add_arguments(self, parser):
        parser.add_argument("-s", "--seed", default=None)
        parser.add_argument("-c", "--club-amount", type=int, default=10)
        parser.add_argument("--skip-clubs", action="store_true")
        parser.add_argument("--skip-settings", action="store_true")

    @transaction.atomic
    def handle(self, *args, **options):
        if options["club_amount"] < 0:
            raise CommandError("--club-amount must be non-negative.")
        seed = str(options["seed"] if options["seed"] is not None else random.randint(10**16, 10**17 - 1))
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
        defaults on first call if it doesn't exist yet. Development contact
        details and related council/page content are populated.
        Connection, CAPTCHA, and image settings are preserved.
        """
        settings_obj = SiteSettings.get_solo()
        settings_obj.maintainance_mode = random_bool()
        settings_obj.school_name = random_string(20)
        settings_obj.school_domain = "example.com"
        settings_obj.school_email = random_email()
        settings_obj.school_phone = random_phone()
        settings_obj.school_mascot = random_string(10)
        settings_obj.school_primary_color = "#122647"
        settings_obj.school_secondary_color = "#47a5bd"
        settings_obj.school_tertiary_color = "#db9820"
        settings_obj.save()
        council = STUCO.get_solo()
        council.council_name = random_string(8)
        council.photo_caption = random_sentence()
        council.save()
        announcements = Announcements.get_solo()
        announcements.ticker_items = "\n".join(random_sentence((4, 8)) for _ in range(3))
        announcements.save()
        for _ in range(3):
            SchoolAnnouncements.objects.update_or_create(
                title=random_sentence((4, 8)),
                defaults={"contents": random_sentence((30, 70))},
            )
        for page_type, label in PageSettings.PageTypes.choices:
            PageSettings.objects.update_or_create(
                internal_site_name=page_type,
                defaults={"title": label, "subtitle": random_string(12),
                          "tagline": random_sentence((10, 20), max_length=200)},
            )
        for social_type, label in SchoolSocialMedia.Sites.choices:
            SchoolSocialMedia.objects.update_or_create(
                site_settings=settings_obj, social_type=social_type,
                defaults={"title": label, "link": random_url()},
            )
        self.stdout.write(f"SiteSettings and council/page settings seeded (pk={settings_obj.pk}).")

    def seed_clubs(self, club_amount: int):
        weekdays = [c[0] for c in Club.WeekDay.choices]
        repetitions = [c[0] for c in Club.Repetition.choices]
        accepting_choices = [c[0] for c in Club.AcceptingApplications.choices]

        for _ in range(club_amount):
            name = f"{random_string(8)} Club"
            club = Club.objects.create(
                name=name,
                preview_description=random_sentence((10, 25), max_length=200),
                description=random_sentence((30, 70), max_length=500),
                repetition=random.choice(repetitions),
                classroom_code=random_string(7),
                accepting_applicants=random.choice(accepting_choices),
                application_form_link=random_url(),
                day_of_meeting=random.choice(weekdays),
                time=random_time(),
                location=f"Room {random.randint(100, 499)}",
                teacher_advisor="Ms. " + random_string(8),
                tagline=random_sentence((3, 8), max_length=30),
                join_instructions=random_sentence((10, 25), max_length=200),
            )

            now = timezone.now()
            ClubAnnouncement.objects.create(
                club=club, title=random_sentence(),
                description=random_sentence((10, 25), max_length=500),
                date_posted=now, expiry=now + datetime.timedelta(days=7),
                popup=random_bool(),
            )

            for _ in range(random.randint(1, 5)):
                club.category.add(random_string(10))

            self.stdout.write(f"  created club '{club.name}' (id={club.id})")
