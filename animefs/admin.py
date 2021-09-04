from django.contrib import admin, messages

from .models import Series


@admin.register(Series)
class SeriesAdmin(admin.ModelAdmin):
    list_display = ["romaji_title", "progress"]
