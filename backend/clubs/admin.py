from typing import Any

from django.contrib import admin
from django import forms
from django.core.exceptions import ValidationError
from django.http import HttpRequest
from taggit.models import Tag
from django.contrib.admin import widgets
from django.contrib.admin.sites import NotRegistered
from django.contrib.sites.models import Site
from .models import Club, ClubAnnouncement
from django.contrib.admin.widgets import RelatedFieldWidgetWrapper
from django.utils.html import format_html
from markdownx.admin import MarkdownxModelAdmin
from django.conf import settings


try:
    admin.site.unregister(Site)
except NotRegistered:
    pass


class ClubsAdminForm(forms.ModelForm):
    category = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=True,
        help_text=format_html(
            "Required.<br>{}",
            "Select up to 3 categories that this club will appear in (e.g 'Engineering' for Robotics Club).",
        ),
        widget=widgets.FilteredSelectMultiple("categories", is_stacked=False)
    )
    day_of_meeting = forms.MultipleChoiceField(
        choices=Club.WeekDay.choices,
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label="Meeting days",
    )

    class Meta:
        model = Club
        fields = [
            'visible', "name", "preview_description", "description", "tagline",  
            "category", "day_of_meeting", "time",
            "repetition", "location", "classroom_code",
            "application_link", "accepting_applicants", "join_instructions",
            "teacher_advisor"
        ]
        widgets = {
            "preview_description": forms.Textarea(attrs={"rows": 3, "cols": 60}),
            "announcement": forms.Textarea(attrs={"rows": 3, "cols": 60}),
            "time": forms.TimeInput(
                attrs={"type": "time", "step": 60},
                format="%H:%M",
            ),
            "tagline": forms.TextInput(attrs={"size": 60}),
            "classroom_code": forms.TextInput(attrs={"size": 20}),
            "location": forms.TextInput(attrs={"size": 10}),
            "application_link": forms.URLInput(attrs={"size": 60}),
            "join_instructions": forms.Textarea(attrs={"rows": 3, "cols": 60})
        }

    def clean_category(self):
        categories = self.cleaned_data["category"]

        maxCategories = settings.MAX_CATEGORIES

        if len(categories) > maxCategories:
            raise ValidationError(
                f"You can select a maximum of {maxCategories} categories."
            )

        return categories

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance and self.instance.pk:
            self.fields['category'].initial = [t.pk for t in self.instance.category.all()]
            self.fields['day_of_meeting'].initial = self.instance.day_of_meeting or []


        tag_rel = Club.category.through._meta.get_field('tag').remote_field

        self.fields['category'].widget = RelatedFieldWidgetWrapper(
            self.fields['category'].widget,
            tag_rel,
            admin.site,
            can_add_related=True
        )

    def save(self, commit=True):
        instance = super().save(commit=False)
        if commit:
            try:
                instance.save()
                instance.category.set(self.cleaned_data.get('category', []))
            except Exception as e:
                raise ValidationError(f"Failed to save: {e}")
        return instance


class ClubAnnouncementAdminForm(forms.ModelForm):
    class Meta:
        model = ClubAnnouncement
        fields = ['title', 'description', 'popup', 'expiry']
        field_classes = {'expiry': forms.DateTimeField}
        widgets = {
            'expiry': forms.DateTimeInput(
                attrs={'type': 'datetime-local', 'step': '1'},
                format='%Y-%m-%dT%H:%M:%S',
            ),
        }


class ClubAnnouncementInline(admin.StackedInline):
    model = ClubAnnouncement
    form = ClubAnnouncementAdminForm
    fields = ['title','description','popup','date_posted','expiry']
    readonly_fields = ['date_posted']
    extra = 0

@admin.register(Club)
class ClubsAdmin(MarkdownxModelAdmin):
    form = ClubsAdminForm
    inlines = [ClubAnnouncementInline]

    class Media:
        css = {'all': ('clubs/club_admin.css',)}
