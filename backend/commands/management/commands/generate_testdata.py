from django.core.management.base import BaseCommand, CommandError
from calendars.models import Calendar, CalendarEvent
from clubs.models import Club
import random
import string
from django.utils import timezone
from datetime import datetime

def random_string(length: int):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

class Command(BaseCommand):
    help = """
    Generates test data procedurally. 

    usage: python3 manage.py generate_testdata [options]

    options:
        -s --seed          specify a seed (default randomly generated 16-digit int)
        -c --club-amount   specify how many instances to generate of the Club model (default 64)
        -e --event-amount  specify how many instances to generate of the CalendarEvent model per calendar (default 64)
    """

    def add_arguments(self, parser):
        parser.add_argument("-s", "--seed")
        parser.add_argument("-c", "--club-amount", type=int)
        parser.add_argument("-e", "--event-amount", type=int)
    
    def handle(self, *args, **options):
        if options["seed"] is None:
            seed = random.randint(10**16, 10**17-1)
        else:
            seed = options["seed"]
        random.seed(seed)
        
        for i in range(options["club_amount"]):
            name = random_string(50)
            description = random_string(100)
            club = Club.objects.create(
                name=name,
                description=description
            )

            for i in range(options["event_amount"]):
                title = random_string(50)
                description = random_string(100)
                start = datetime.fromtimestamp(random.randint(int(datetime.now().timestamp()), int(datetime.now().timestamp()+31556926)))
                end = datetime.fromtimestamp(random.randint(int(start.timestamp()), int(start.timestamp()+31556926)))
                location = random_string(100)
                calendar = club.calendar
                CalendarEvent.objects.create(
                    title=title,
                    description=description,
                    start=start,
                    end=end,
                    location=location,
                    calendar=calendar
                )
        
        self.stdout.write(f"Done with seed {seed}.")

