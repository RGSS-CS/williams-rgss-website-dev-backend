from django.contrib import admin
from django import forms
from taggit.models import Tag
from .models import Club, ClubGalleryImage


class EventAdminForm(forms.ModelForm):
    category = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False,
        widget=admin.widgets.FilteredSelectMultiple(
            verbose_name="Categories", is_stacked=False
        )
    )

    class Meta:
        model = Club
        fields = [
            "name", "preview_description", "description", "tagline", "category",
            "day_of_meeting", "time", "repetition", "room_num",
            "classroom_code", "accepting_applicants", "application_form_link", "teacher_advisor",
        ]
        widgets = {
            'time': forms.TimeInput(format='%H:%M', attrs={'type': 'time'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            # initial expects a list of PKs for ModelMultipleChoiceField
            self.fields['category'].initial = [t.pk for t in self.instance.category.all()]

    def save(self, commit=True):
        instance = super().save(commit=False)
        # Save instance first so TaggableManager has a PK
        if commit:
            instance.save()
            instance.category.set(self.cleaned_data.get('category', []))
        return instance


@admin.register(Club)
class EventAdmin(admin.ModelAdmin):
    form = EventAdminForm


admin.site.register(ClubGalleryImage)