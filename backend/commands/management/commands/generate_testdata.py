"""Seed randomized development clubs and site settings."""

import datetime
import random
import string

from django.core.management.base import BaseCommand

from clubs.models import Club
from management.models import SiteSettings


def random_string(length: int) -> str:
    return "".join(random.choices(string.ascii_letters + string.digits, k=length))


def random_bool() -> bool:
    return random.choice([True, False])


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


class Command(BaseCommand):
    help = "Seed randomized development clubs and site settings."

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
        settings_obj.school_primary_color = "#122647"
        settings_obj.school_secondary_color = "#47a5bd"
        settings_obj.school_tertiary_color = "#db9820"
        settings_obj.save()
        self.stdout.write(f"SiteSettings seeded (pk={settings_obj.pk}).")

    def seed_clubs(self, club_amount: int):
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
                day_of_meeting=random.choice(weekdays),
                time=random_time(),
                room_number=random.randint(100, 499),
                teacher_advisor="Mr./Mrs./Ms. " + random_string(8),
                tagline=random_sentence((3, 8)),
                join_instructions=random_sentence((10, 25)),
            )

            for _ in range(random.randint(1, 5)):
                club.category.add(random_string(10))

            self.stdout.write(f"  created club '{club.name}' (id={club.id})")
