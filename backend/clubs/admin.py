from django.contrib import admin
from django import forms
from django.core.exceptions import ValidationError
from django.forms.widgets import CheckboxSelectMultiple
from taggit.models import Tag
from django.contrib.admin import widgets
from django.contrib.admin.sites import NotRegistered
from django.contrib.sites.models import Site
from .models import Club, ClubWhyJoin
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
            "name",
            "preview_description",
            "description",
            "tagline",
            "category",
            "image",
            "day_of_meeting",
            "time",
            "repetition",
            "room_number",
            "announcement",
            "classroom_code",
            "application_form_link",
            "join_instructions",
            "accepting_applicants",
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


@admin.register(Club)
class ClubsAdmin(admin.ModelAdmin):
    form = ClubsAdminForm
    inlines = [WhyJoinInline]
    readonly_fields = ("gallery_admin_link",)

    def gallery_admin_link(self, obj):
        from django.urls import reverse
        from django.utils.html import format_html

        if not obj.gallery:
            return "Save this club once to create its gallery."
        url = reverse("admin:photologue_gallery_change", args=[obj.gallery.pk])
        return format_html('<a href="{}">Manage photos for this gallery</a>', url)

    gallery_admin_link.short_description = "Photo gallery"

    def save_model(self, request, obj, form, change):
        from photologue.models import Gallery

        if not obj.gallery_id:
            obj.gallery = Gallery.objects.create(title=f"{obj.name or 'Club'} Gallery")

        try:
            obj.full_clean()
            super().save_model(request, obj, form, change)
        except ValidationError as e:
            form.add_error(None, e)