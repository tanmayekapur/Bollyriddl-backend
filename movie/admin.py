from import_export.admin import ImportExportMixin
from django.contrib import admin
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
