from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('clubs', '0012_remove_club_visable_club_visible_and_more'),
    ]

    operations = [
        migrations.DeleteModel(name='ClubChanges'),
        migrations.DeleteModel(name='ClubMembership'),
    ]
