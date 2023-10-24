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
)

# Register your models here.


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    list_display_links = list_display
    search_fields = ("name",)


@admin.register(Cast)
class CastAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    list_display_links = list_display
    search_fields = ("name",)


@admin.register(Writer)
class WriterAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    list_display_links = list_display
    search_fields = ("name",)


@admin.register(Director)
class DirectorAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    list_display_links = list_display
    search_fields = ("name",)


@admin.register(MusicDirector)
class MusicDirectorAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    list_display_links = list_display
    search_fields = ("name",)


@admin.register(ProductionHouse)
class ProductionHouseAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    list_display_links = list_display
    search_fields = ("name",)


@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "year", "director")
    list_display_links = list_display
    search_fields = ("name", "imdb_id", "director__name")
    filter_horizontal = ("genres", "cast", "writers", "music_directors")
    autocomplete_fields = ("director", "production_house")


@admin.register(Archive)
class ArchiveAdmin(admin.ModelAdmin):
    list_display = ("id", "date", "movie")
    list_display_links = list_display
    search_fields = ("date", "movie__name")
    autocomplete_fields = ("movie",)
