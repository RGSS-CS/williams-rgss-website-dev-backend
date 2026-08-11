from django.contrib import admin
from django import forms
from .models import UserJoinCode
from django.contrib.admin import widgets

class UserJoinCodeForm(forms.ModelForm):
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
            'expiry': widgets.AdminSplitDateTime(attrs={'type': 'datetime-local'}),
        }

@admin.register(UserJoinCode)
class UserJoinCodeAdmin(admin.ModelAdmin):
    form = UserJoinCodeForm
    readonly_fields = ('code', 'uses', 'created', 'updated')