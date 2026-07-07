from django.contrib import admin
from django import forms
from django.core.exceptions import ValidationError
from taggit.models import Tag
from django.contrib.admin.widgets import FilteredSelectMultiple
from .models import Club, ClubGalleryImage, ClubWhyJoin


class EventAdminForm(forms.ModelForm):
    category = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False,
        widget=FilteredSelectMultiple(
            verbose_name="Categories",
            is_stacked=False,
        ),
    )

    class Meta:
        model = Club
        fields = [
            "name", "preview_description", "description", "tagline", "category",
            "day_of_meeting", "time", "repetition", "room_num", "announcement",
            "classroom_code", "accepting_applicants", "application_form_link", "teacher_advisor",
        ]
        widgets = {
            "time": forms.TimeInput(
                format="%H:%M",
                attrs={"type": "time"},
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance and self.instance.pk:
            self.fields['category'].initial = [t.pk for t in self.instance.category.all()]

    def save(self, commit=True):
        instance = super().save(commit=False)
        if commit:
            try:
                instance.save()
                instance.category.set(self.cleaned_data.get('category', []))
            except Exception as e:
                raise ValidationError(f"Failed to save: {e}")
        return instance


class WhyJoinInline(admin.TabularInline):  # or admin.StackedInline
    model = ClubWhyJoin
    extra = 1


@admin.register(Club)
class EventAdmin(admin.ModelAdmin):
    form = EventAdminForm
    def save_model(self, request, obj, form, change):
        try:
            # Run full model-level validation before saving
            obj.full_clean()
            super().save_model(request, obj, form, change)
        except ValidationError as e:
            # Attach the error to the form so admin re-renders with fields intact
            form.add_error(None, e)