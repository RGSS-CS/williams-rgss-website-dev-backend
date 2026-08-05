from django.contrib import admin
from .models import UserJoinCode

@admin.register(UserJoinCode)
class UserJoinCodeAdmin(admin.ModelAdmin):
    readonly_fields = ('code', 'uses', 'created', 'updated')