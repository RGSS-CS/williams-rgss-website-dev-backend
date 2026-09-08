from django.contrib import admin
from django.contrib.admin.widgets import AdminFileWidget
from .models import Photos, Videos, MassImport
from django import forms
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import UploadedFile
import puremagic
from PIL import Image
import zipfile

def validate_upload_mime(file, allowed_types):
    try:
        file.seek(0)
        mime = puremagic.from_string(file.read(1024), mime=True)
    except (puremagic.PureError, ValueError) as exc:
        raise ValidationError('Unable to identify the uploaded file type.')

    file.seek(0)
    if mime not in allowed_types:
        raise ValidationError(f'Invalid file type. Allowed types: {allowed_types}')

class PhotoAdminForm(forms.ModelForm):   
    image = forms.ImageField(widget=AdminFileWidget())

    def clean_image(self):
        #Check File Size
        file = self.cleaned_data['image']
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

                min_dim = (100,100)
                max_dim = (10000,10000)
                if (width < min_dim[0] or height < min_dim[1]):
                    raise ValidationError(f'Image too small. Min dimensions: {min_dim[0]}x{min_dim[1]}')
                if (width > max_dim[0] or height > max_dim[1]):
                    raise ValidationError(f'Image is too large. Max dimensions: {max_dim[0]}x{max_dim[1]}')
        except (IOError, SyntaxError) as e:
            raise ValidationError(f'Invalid image file: {str(e)}')

        file.seek(0)
        
        return file
    
@admin.register(Photos)
class PhotoAdmin(admin.ModelAdmin):
    fields = ('name', 'description', 'image', 'club', 'created_date', 'modified_date')
    readonly_fields = ('created_date','modified_date')
    form = PhotoAdminForm

    def get_form(self, request, obj=None, **kwargs):
        form = super(PhotoAdmin, self).get_form(request, obj, **kwargs)

        field = form.base_fields['club']
        field.widget.can_add_related = False
        field.widget.can_change_related = False
        field.widget.can_delete_related = False
        field.widget.can_view_related = False

        return form

############################## VIDEO FILES ####################################

class VideoAdminForm(forms.ModelForm):
    video_file = forms.FileField(required=False, widget=AdminFileWidget())

    def clean_video_file(self):
        file = self.cleaned_data['video_file']
        if not isinstance(file, UploadedFile):
            return file

        max_size = 4 * 1024 ** 3
        if file.size > max_size:
            raise ValidationError('The video file is too large. The max size is 4 GiB.')

        allowed_mime = ['video/mp4', 'video/x-matroska', 'video/quicktime']
        validate_upload_mime(file, allowed_mime)

        return file


@admin.register(Videos)
class VideoAdmin(admin.ModelAdmin):
    fields = ('name', 'description','link', 'video_file', 'club', 'created_date', 'modified_date')
    readonly_fields = ('created_date','modified_date')
    form = VideoAdminForm

    def get_form(self, request, obj=None, **kwargs):
        form = super(VideoAdmin, self).get_form(request, obj, **kwargs)

        field = form.base_fields['club']
        field.widget.can_add_related = False
        field.widget.can_change_related = False
        field.widget.can_delete_related = False
        field.widget.can_view_related = False

        return form


############################## ZIP Files ##############################

@admin.register(MassImport)
class MassImportAdmin(admin.ModelAdmin):
    fields = ('name','zip_file', 'file_type', 'club','upload_date','upload_status')
    readonly_fields = ('upload_status','name','upload_date')

    def get_form(self, request, obj=None, **kwargs):
        form = super(MassImportAdmin, self).get_form(request, obj, **kwargs)

        field = form.base_fields['club']
        field.widget.can_add_related = False
        field.widget.can_change_related = False
        field.widget.can_delete_related = False
        field.widget.can_view_related = False

        return form