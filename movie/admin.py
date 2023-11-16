from import_export.admin import ImportExportMixin
from django.contrib import admin, messages
import datetime
import random

from .models import (
    Genre,
    Cast,
    Writer,
    Director,
    MusicDirector,
    ProductionHouse,
    Movie,
    Archive,
    Contact,
    Feedback,
    FeedbackSubject,
)

# Register your models here.


@admin.register(Genre)
class GenreAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = ("id", "name")
    list_display_links = list_display
    search_fields = ("name",)


@admin.register(Cast)
class CastAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = ("id", "name")
    list_display_links = list_display
    search_fields = ("name",)


@admin.register(Writer)
class WriterAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = ("id", "name")
    list_display_links = list_display
    search_fields = ("name",)


@admin.register(Director)
class DirectorAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = ("id", "name")
    list_display_links = list_display
    search_fields = ("name",)


@admin.register(MusicDirector)
class MusicDirectorAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = ("id", "name")
    list_display_links = list_display
    search_fields = ("name",)


@admin.register(ProductionHouse)
class ProductionHouseAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = ("id", "name")
    list_display_links = list_display
    search_fields = ("name",)


@admin.register(Movie)
class MovieAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = ("id", "name", "year", "director")
    list_display_links = list_display
    search_fields = ("name", "imdb_id", "director__name")
    filter_horizontal = ("genres", "cast", "writers", "music_directors")
    autocomplete_fields = ("director", "production_house")
    actions = ("set_mystery_movie",)

    @admin.action(description="Set mystery movie for today")
    def set_mystery_movie(self, request, queryset):
        today = datetime.date.today()
        if Archive.objects.filter(date=today).exists():
            self.message_user(
                request, "Mystery movie is already set for today.", messages.WARNING
            )
        else:
            mystery_movie = random.choice(list(queryset))
            Archive.objects.create(movie=mystery_movie, date=today)
            self.message_user(
                request, "Mystery movie is set for today.", messages.SUCCESS
            )


@admin.register(Archive)
class ArchiveAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = ("id", "date", "movie")
    list_display_links = list_display
    search_fields = ("date", "movie__name")
    autocomplete_fields = ("movie",)


@admin.register(Contact)
class ContactAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = ("id", "name", "email", "short_subject")
    list_display_links = list_display
    search_fields = ("name", "email", "subject")

    def short_subject(self, obj):
        max_length = 50
        if len(obj.subject) > max_length:
            return obj.subject[:max_length] + "..."
        else:
            return obj.subject

    short_subject.short_description = "subject"


@admin.register(Feedback)
class FeedbackAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = ("id", "email", "subjects_list")
    list_display_links = list_display
    search_fields = ("email", "subjects__name")
    filter_horizontal = ("subjects",)

    def subjects_list(self, obj):
        return ", ".join([subject.name for subject in obj.subjects.all()])

    subjects_list.short_description = "subjects"


@admin.register(FeedbackSubject)
class FeedbackSubjectAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = ("id", "name")
    list_display_links = list_display
    search_fields = ("name",)
