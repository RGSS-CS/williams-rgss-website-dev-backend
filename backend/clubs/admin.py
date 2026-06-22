from django.contrib import admin
from django import forms
from taggit.models import Tag
from django.contrib.admin.widgets import FilteredSelectMultiple
from .models import Club, ClubGalleryImage, WhyJoin


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
            "name",
            "preview_description",
            "description",
            "category",
            "day_of_meeting",
            "time",
            "repetition",
            "room_num",
            "classroom_code",
            "teacher_advisor",
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
            self.fields["category"].initial = [
                t.pk for t in self.instance.category.all()
            ]

    def save(self, commit=True):
        instance = super().save(commit=False)

        if commit:
            instance.save()
            instance.category.set(
                self.cleaned_data.get("category", [])
            )

        return instance


class WhyJoinInline(admin.TabularInline):  # or admin.StackedInline
    model = WhyJoin
    extra = 1


@admin.register(Club)
class EventAdmin(admin.ModelAdmin):
    form = EventAdminForm
    inlines = [WhyJoinInline]


admin.site.register(ClubGalleryImage)