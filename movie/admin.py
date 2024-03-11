from sortedm2m_filter_horizontal_widget.forms import SortedFilteredSelectMultiple
from import_export.admin import ImportExportMixin
from django.contrib import admin, messages
import datetime
import random

from .resources import MovieResource, UserActivityResource
from .mixins import AnalyticsMixin, ArchiveMixin
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
    Guess,
    UserActivity,
    User,
)

# Register your models here.

admin.site.site_title = "Movie Guessing Game site admin"
admin.site.site_header = "Movie Guessing Game Administration"


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
    list_display = ("id", "name", "year")
    list_display_links = list_display
    search_fields = ("name", "imdb_id", "year")
    filter_horizontal = (
        "genres",
        "cast",
        "writers",
        "directors",
        "music_directors",
        "production_houses",
    )
    actions = ("set_mystery_movie",)
    resource_class = MovieResource

    def formfield_for_manytomany(self, db_field, request=None, **kwargs):
        if db_field.name in self.filter_horizontal:
            kwargs["widget"] = SortedFilteredSelectMultiple()
        return super().formfield_for_manytomany(db_field, request, **kwargs)

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
class ArchiveAdmin(ArchiveMixin, ImportExportMixin, admin.ModelAdmin):
    list_display = ("id", "date", "movie")
    list_display_links = list_display
    search_fields = ("date", "movie__name")
    ordering = ("-date",)
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

    def formfield_for_manytomany(self, db_field, request=None, **kwargs):
        if db_field.name in self.filter_horizontal:
            kwargs["widget"] = SortedFilteredSelectMultiple()
        return super().formfield_for_manytomany(db_field, request, **kwargs)

    def subjects_list(self, obj):
        return ", ".join([subject.name for subject in obj.subjects.all()])

    subjects_list.short_description = "subjects"


@admin.register(FeedbackSubject)
class FeedbackSubjectAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = ("id", "name")
    list_display_links = list_display
    search_fields = ("name",)


class GuessInline(admin.TabularInline):
    model = Guess
    extra = 0
    max_num = 0
    can_delete = False
    exclude = ("id", "order")


@admin.register(UserActivity)
class UserActivityAdmin(AnalyticsMixin, ImportExportMixin, admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "start_time",
        "archive_id",
        "total_time",
        "guessed_movies_count",
        "winner_display",
    )
    list_display_links = list_display
    search_fields = ("user__uuid",)
    readonly_fields = ("guessed_movies_count", "total_time", "winner_display")
    inlines = [GuessInline]
    resource_class = UserActivityResource

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = [field.name for field in self.model._meta.fields]
        readonly_fields.remove("id")
        return readonly_fields + list(self.readonly_fields)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def winner_display(self, obj):
        return obj.winner

    winner_display.boolean = True
    winner_display.short_description = "winner"


@admin.register(User)
class UserAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = ("id", "uuid", "email")
    list_display_links = list_display
    search_fields = ("uuid", "email")
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False
