from django.db import migrations, models


def convert_meeting_day_to_list(apps, schema_editor):
    Club = apps.get_model("clubs", "Club")
    for club in Club.objects.all().iterator():
        value = club.day_of_meeting
        if isinstance(value, str):
            club.day_of_meeting = [value] if value else []
            club.save(update_fields=["day_of_meeting"])


def convert_meeting_days_to_single(apps, schema_editor):
    Club = apps.get_model("clubs", "Club")
    for club in Club.objects.all().iterator():
        value = club.day_of_meeting
        if isinstance(value, list):
            club.day_of_meeting = value[0] if value else None
            club.save(update_fields=["day_of_meeting"])


class Migration(migrations.Migration):
    dependencies = [("clubs", "0023_alter_club_tagline")]

    operations = [
        migrations.AlterField(
            model_name="club",
            name="day_of_meeting",
            field=models.JSONField(blank=True, default=list),
        ),
        migrations.RunPython(
            convert_meeting_day_to_list,
            reverse_code=convert_meeting_days_to_single,
        ),
    ]
