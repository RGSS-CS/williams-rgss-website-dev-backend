from django.contrib import admin
from django.contrib.admin.widgets import AdminFileWidget
from .models import Photos, Videos
from django import forms
from django.core.exceptions import ValidationError
import magic
from PIL import Image

class PhotoAdminForm(forms.ModelForm):   
    image = forms.ImageField(widget=AdminFileWidget())

    def clean_photo(self):
        #Check File Size
        file = self.cleaned_data['image']
        max_size = 2.5 * 1024 * 1024
        if file.size > max_size:
            raise ValidationError(f'The image is too large. Max size is 2.5MB')

        #Check MIME Types
        
        allowed_mime_types = ['image/jpeg','image/png', 'image/webp', 'image/jpg']
        mime = magic.from_buffer(file.read(1024), mime=True) # Read first 1KB for MIME detection  
        file.seek(0) # Reset file pointer for subsequent processing  

        if mime not in allowed_mime_types:
            raise ValidationError(f'Invalid file type. Allowed types: {allowed_mime_types}')

        #Validatate Content with Pillow
        try:
            with Image.open(file) as img:
                img.verify() # check for corruption
                img.seek(0) #reset for dimension check

                min_dim = (100,100)
                max_dim = (4000,4000)
                width, height = img.size
                if (width < min_dim[0] or height < min_dim[1]):
                    raise ValidationError(f'Image too small. Min dimensions: {min_dim[0]}x{min_dim[1]}')
                if (width > max_dim[0] or height > max_dim[1]):
                    raise ValidationError(f'Image is too large. Max dimensinos: {max_dim[0]}x{max_dim[1]}')
        except (IOError, SyntaxError) as e:
            raise ValidationError(f'Invalid image file: {str(e)}')
        
        return file
    
@admin.register(Photos)
class PhotoAdmin(admin.ModelAdmin):
    fields = ('name', 'description', 'image', 'club', 'created_date', 'modified_date')
    readonly_fields = ('created_date','modified_date')
    form = PhotoAdminForm

############################## VIDEO FILES ####################################

class VideoAdminForm(forms.ModelForm):
    video_file = forms.FileField(required=False, widget=AdminFileWidget())

    def clean_video(self):
        file = self.cleaned_data['video_file']

        max_size = 4 * 1024 ** 3
        if file.size > max_size:
            raise ValidationError('The video file is too large. The max size is 4 GiB.')

        allowed_mime = ['video/mp4', 'video/mkv', 'video/mov']
        mime = magic.from_buffer(file.read(1024), mime=True)
        file.seek(0)

        if mime not in allowed_mime:
            raise ValidationError(f'Invalid file type. Allowed types: {allowed_mime}')

        return file


@admin.register(Videos)
class VideoAdmin(admin.ModelAdmin):
    fields = ('name', 'description','link', 'video_file', 'club', 'created_date', 'modified_date')
    readonly_fields = ('created_date','modified_date')
    form = VideoAdminForm
