from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('clubs', '0007_remove_clubannouncement_pinned_and_more'),
    ]

    operations = [
        migrations.RemoveField(model_name='club', name='gallery'),
        migrations.DeleteModel(name='GalleryExtended'),
    ]
