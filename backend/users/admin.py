from django.contrib import admin
from django import forms
from .models import UserJoinCode
from django.utils.html import format_html
import qrcode
import io
import base64
from management.models import SiteSettings

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
            'uses',
        ]
        widgets = {
            'label': forms.TextInput(attrs={'size': 40}),
            'description': forms.Textarea(attrs={'rows': 4, 'cols': 60}),
        }

@admin.register(UserJoinCode)
class UserJoinCodeAdmin(admin.ModelAdmin):
    form = UserJoinCodeForm
    readonly_fields = ('code', 'code_preview', 'uses', 'created', 'updated')

    def code_preview(self, obj) -> str:
        if obj.code:
            frontend_url = SiteSettings.get_solo().frontend_url
            url = f"{frontend_url}/private/register?rel={obj.code}"
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