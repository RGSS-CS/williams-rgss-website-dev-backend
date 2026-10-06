from django.core.exceptions import ValidationError
from django.tasks import task

from galleries.models import MassImport
from .services.unzip import import_zip_photos

@task(queue_name='unzip_media')
def import_mass_upload(mass_import_id):
    upload = MassImport.objects.get(pk=mass_import_id)

    try: 
        upload.upload_status = "RUN"
        upload.save(update_fields=['upload_status'])
        
        import_zip_photos(upload)

        upload.upload_status = 'DONE'
        upload.save(update_fields=['upload_status'])

    except(ValidationError, OSError):
        upload.upload_status = 'ERROR'
        upload.save(update_fields=['upload_status'])
        raise