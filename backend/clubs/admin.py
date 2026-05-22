from django.contrib import admin
from django import forms
from taggit.models import Tag
from .models import Club, ClubGalleryImage

class EventAdminForm(forms.ModelForm):
    categories = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=True,
        widget=admin.widgets.FilteredSelectMultiple(
            verbose_name="Categories", is_stacked=False
        )
    )
    class Meta:
        model = Club
        fields = [
            "name", "description",
            "day_of_meeting", "time", "room_num",
            "classroom_code", "teacher_advisor"
        ]
        widgets = {
            'time' : forms.TimeInput(format='%H:%M', attrs={'type': 'time'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['tags'].initial = self.instance.category.all()
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        if commit:
            instance.tags.save(self.cleaned_data['tags'])
        return instance

@admin.register(Club)
class EventAdmin(admin.ModelAdmin):
    form = EventAdminForm

admin.site.register(ClubGalleryImage)