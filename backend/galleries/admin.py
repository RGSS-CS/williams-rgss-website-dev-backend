from django.contrib import admin
from django.contrib.admin.widgets import AdminFileWidget
from .models import Photos, MassImport
from django import forms
from .validators import validate_image_upload

class PhotoAdminForm(forms.ModelForm):
    image = forms.ImageField(widget=AdminFileWidget())

    def clean_image(self):
        return validate_image_upload(self.cleaned_data['image'])

@admin.register(Photos)
class PhotoAdmin(admin.ModelAdmin):
    fields = ('name', 'description', 'image', 'club','shown_in_gallery','shown_in_main_page', 'created_date', 'modified_date')
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
