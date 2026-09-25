import management.models
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('management', '0006_alter_sitesettings_maintainance_mode'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sitesettings',
            name='favicon',
            field=models.ImageField(
                upload_to=management.models.FaviconRename,
                help_text='This is the icon that appears in the browser tab. '
                'It should be a square image, preferably 32x32 pixels.',
            ),
        ),
        migrations.AlterField(
            model_name='sitesettings',
            name='site_logo',
            field=models.ImageField(
                upload_to=management.models.SiteLogoRename,
                help_text='This is the icon that represents your school. This image will be displayed on the navigation bar and the homepage.',
            ),
        ),
    ]
