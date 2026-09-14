from django.contrib import admin
from .models import STUCO, Ticker
from solo.admin import SingletonModelAdmin
from django import forms
from django.contrib.admin import widgets

class STUCOAdminForm(forms.ModelForm):
    class Meta:
        model = STUCO
        fields = [
            'council_name', 'group_photo'
        ]
    

@admin.register(STUCO)
class STUCOAdmin(SingletonModelAdmin):
    form = STUCOAdminForm

admin.site.register(Ticker)