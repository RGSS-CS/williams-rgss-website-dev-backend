from django.contrib import admin
from django import forms
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
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

class CustomUserAdmin(UserAdmin):
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2'),
        }),
    )

admin.site.unregister(User)
admin.site.register(User, UserAdmin)