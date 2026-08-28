from typing import Any

from django.contrib import admin
from django import forms
from django.core.exceptions import ValidationError
from django.forms.widgets import CheckboxSelectMultiple
from django.http import HttpRequest
from taggit.models import Tag
from django.contrib.admin import widgets
from django.contrib.admin.sites import NotRegistered
from django.contrib.sites.models import Site
from .models import Club, ClubWhyJoin, GalleryExtended, ClubMembership
from django.contrib.admin.widgets import RelatedFieldWidgetWrapper


try:
    admin.site.unregister(Site)
except NotRegistered:
    pass


class ClubsAdminForm(forms.ModelForm):
    category = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=True,
        help_text="The 'Category' that this club will appear in (e.g 'Engineering' for Robotics Club)",
        widget=CheckboxSelectMultiple()
    )

    class Meta:
        model = Club
        fields = [
            "name", "preview_description", "description", "tagline",  
            "category", "gallery", "day_of_meeting", "time",        
            "repetition", "room_number", "announcement", "classroom_code",
            "application_form_link", "join_instructions", "accepting_applicants",
            "teacher_advisor"
        ]
        widgets = {
            "time": forms.TimeInput(attrs={"type": "time"}, format="%H:%M"),
            "preview_description": forms.Textarea(attrs={"rows": 3, "cols": 60}),
            "description": forms.Textarea(attrs={"rows": 6, "cols": 80}),
            "announcement": forms.Textarea(attrs={"rows": 3, "cols": 60}),
            "tagline": forms.TextInput(attrs={"size": 60}),
            "classroom_code": forms.TextInput(attrs={"size": 20}),
            "room_number": forms.TextInput(attrs={"size": 10}),
            "application_form_link": forms.URLInput(attrs={"size": 60}),
            "join_instructions": forms.Textarea(attrs={"rows": 3, "cols": 60}),
        }

    def clean_category(self):
        categories = self.cleaned_data["category"]

        MAX_CATEGORIES = 3

        if len(categories) > MAX_CATEGORIES:
            raise ValidationError(
                f"You can select a maximum of {MAX_CATEGORIES} categories."
            )

        return categories

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance and self.instance.pk:
            self.fields['category'].initial = [t.pk for t in self.instance.category.all()]


        tag_rel = Club.category.through._meta.get_field('tag').remote_field

        self.fields['category'].widget = RelatedFieldWidgetWrapper(
            self.fields['category'].widget,
            tag_rel,
            admin.site,
            can_add_related=True,
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



    
class WhyJoinInline(admin.TabularInline):
    model = ClubWhyJoin
    extra = 1


class ClubMemberInline(admin.TabularInline):
    model = ClubMembership
    extra = 1
    fields = ("user", "role", "bypass_confirmation_restrictions")

    def has_add_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser


@admin.register(Club)
class ClubsAdmin(admin.ModelAdmin):
    form = ClubsAdminForm
    inlines = [WhyJoinInline]

@admin.register(ClubMembership)
class ClubMembershipAdmin(admin.ModelAdmin):
    list_display = ("user", "club", "role", "bypass_confirmation_restrictions", "updated")