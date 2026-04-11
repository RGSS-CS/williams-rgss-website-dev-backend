from django.db import models

class Club(models.Model):
    WEEKDAY_CHOICES = [
        ("monday", "Monday"),
        ("tuesday", "Tuesday"),
        ("wednesday", "Wednesday"),
        ("thursday", "Thursday"),
        ("friday", "Friday"),
    ]

    name = models.CharField(max_length=100)
    description = models.TextField()
    day = models.CharField(max_length=10, choices=WEEKDAY_CHOICES, default="monday")
    classroom_code = models.CharField(max_length=10)

    def __str__(self):
        return self.name


class School_event(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    # NEW: link each event to a club
    club = models.ForeignKey(Club, on_delete=models.CASCADE, related_name="events")

    def __str__(self):
        return self.title
