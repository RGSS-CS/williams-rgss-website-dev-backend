from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import UploadedFile
from PIL import Image
import puremagic


def validate_upload_mime(file, allowed_types):
    try:
        file.seek(0)
        mime = puremagic.from_string(file.read(1024), mime=True)
    except (puremagic.PureError, ValueError) as exc:
        raise ValidationError('Unable to identify the uploaded file type.')
    finally:
        file.seek(0)

    if mime not in allowed_types:
        raise ValidationError(f'Invalid file type. Allowed types: {allowed_types}')

def validate_image_upload(file, min_dim=(100, 100)):
    #Check File Size
    if not isinstance(file, UploadedFile):
        return file
    max_size = 2.5 * 1024 * 1024
    if file.size > max_size:
        raise ValidationError(f'The image is too large. Max size is 2.5MB')

    #Check MIME Types
    
    allowed_mime_types = ['image/jpeg', 'image/png', 'image/webp']
    validate_upload_mime(file, allowed_mime_types)

    #Validatate Content with Pillow
    try:
        with Image.open(file) as img:
            width, height = img.size
            img.verify() # check for corruption

            max_dim = (10000,10000)
            if (width < min_dim[0] or height < min_dim[1]):
                raise ValidationError(f'Image too small. Min dimensions: {min_dim[0]}x{min_dim[1]}')
            if (width > max_dim[0] or height > max_dim[1]):
                raise ValidationError(f'Image is too large. Max dimensions: {max_dim[0]}x{max_dim[1]}')
    except (IOError, SyntaxError) as e:
        raise ValidationError(f'Invalid image file: {str(e)}')
    finally:
        file.seek(0)
    
    return file
