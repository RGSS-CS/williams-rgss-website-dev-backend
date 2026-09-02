from django.contrib import admin
from django import forms
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser
from .models import UserJoinCode
from django.utils.html import format_html
import qrcode
import io
import base64
from management.models import SiteSettings
from django.core.exceptions import PermissionDenied
from django.conf import settings
from cryptography.fernet import Fernet

class UserJoinCodeForm(forms.ModelForm):
    expiry = forms.DateTimeField(widget=forms.DateTimeInput(attrs={'type':'datetime-local'}))
    class Meta:
        model = UserJoinCode
        fields = [
            'enabled',
            'label',
            'description',
            'expiry',
            'max_uses',
            'uses'
        ]
        widgets = {
            'label': forms.TextInput(attrs={'size': 40}),
            'description': forms.Textarea(attrs={'rows': 4, 'cols': 60})
        }

@admin.register(UserJoinCode)
class UserJoinCodeAdmin(admin.ModelAdmin):
    form = UserJoinCodeForm
    readonly_fields = ('code', 'code_preview', 'code_url', 'uses', 'created', 'updated')

    def code_preview(self, obj) -> str:
        if obj.code:
            frontend_url = SiteSettings.get_solo().frontend_url
            f = Fernet(settings.FERNET_KEY.encode())
            token = f.encrypt(obj.code.encode())
            url = f"{frontend_url}/private/authentication/register?rel='{token}'"
            qr = qrcode.make(url)
            buffer = io.BytesIO()
            qr.save(buffer, format="PNG")

            qr_b64 = base64.b64encode(buffer.getvalue()).decode('utf-8')

            return format_html(
                '<img src="data:image/png;base64,{}" style="max-height: 200px;" />',
                qr_b64
            )
        else:
            return "Error: it seems that the code field is null, or in Python, None. This shouldn't have happened."

    def code_url(self, obj):
        if obj.code:
            frontend_url = SiteSettings.get_solo().frontend_url
            f = Fernet(settings.FERNET_KEY.encode())
            token = f.encrypt(obj.code.encode())
            url = f"{frontend_url}/private/authentication/register?rel='{token}'"
            return url
        else:
            return "Error: it seems that the code field is null, or in Python, None. This shouldn't have happened."


############################################# FOR CUSTOM USER ADMINISTRATION #############################################


class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'first_name', 'last_name', 'password1', 'password2'),
        }),
    )

admin.site.register(CustomUser, CustomUserAdmin)