from sortedm2m_filter_horizontal_widget.forms import SortedFilteredSelectMultiple
from import_export.admin import ImportExportMixin
from django.contrib import admin, messages
import datetime
import random

from .resources import MovieResource, UserActivityResource, ArchiveResource
from .mixins import AnalyticsMixin, ArchiveMixin
from .forms import SelectiveExportForm
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

# Set custom titles for admin site
admin.site.site_title = "Movie Guessing Game site admin"
admin.site.site_header = "Movie Guessing Game Administration"


# Register Genre model with ImportExportMixin to enable import/export functionality
@admin.register(Genre)
class GenreAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = ("id", "name")
    list_display_links = list_display
    search_fields = ("name",)


# Register Cast model with ImportExportMixin
@admin.register(Cast)
class CastAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = ("id", "name")
    list_display_links = list_display
    search_fields = ("name",)


# Register Writer model with ImportExportMixin
@admin.register(Writer)
class WriterAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = ("id", "name")
    list_display_links = list_display
    search_fields = ("name",)


# Register Director model with ImportExportMixin
@admin.register(Director)
class DirectorAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = ("id", "name")
    list_display_links = list_display
    search_fields = ("name",)


# Register MusicDirector model with ImportExportMixin
@admin.register(MusicDirector)
class MusicDirectorAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = ("id", "name")
    list_display_links = list_display
    search_fields = ("name",)


# Register ProductionHouse model with ImportExportMixin
@admin.register(ProductionHouse)
class ProductionHouseAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = ("id", "name")
    list_display_links = list_display
    search_fields = ("name",)


# Register Movie model with ImportExportMixin and custom admin actions
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

    # Customize the form field for many-to-many relationships
    def formfield_for_manytomany(self, db_field, request=None, **kwargs):
        if db_field.name in self.filter_horizontal:
            kwargs["widget"] = SortedFilteredSelectMultiple()
        return super().formfield_for_manytomany(db_field, request, **kwargs)

    # Custom admin action to set mystery movie for today
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


# Register Archive model with ArchiveMixin and ImportExportMixin
@admin.register(Archive)
class ArchiveAdmin(ArchiveMixin, ImportExportMixin, admin.ModelAdmin):
    list_display = ("id", "archive_id", "date", "movie")
    list_display_links = list_display
    search_fields = ("date", "movie__name")
    ordering = ("-date",)
    autocomplete_fields = ("movie",)
    resource_class = ArchiveResource


# Register Contact model with ImportExportMixin
@admin.register(Contact)
class ContactAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = ("id", "name", "email", "short_subject")
    list_display_links = list_display
    search_fields = ("name", "email", "subject")

    # Method to display a short subject in the admin list view
    def short_subject(self, obj):
        max_length = 50
        if len(obj.subject) > max_length:
            return obj.subject[:max_length] + "..."
        else:
            return obj.subject

    short_subject.short_description = "subject"


# Register Feedback model with ImportExportMixin
@admin.register(Feedback)
class FeedbackAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = ("id", "email", "subjects_list")
    list_display_links = list_display
    search_fields = ("email", "subjects__name")
    filter_horizontal = ("subjects",)

    # Customize the form field for many-to-many relationships
    def formfield_for_manytomany(self, db_field, request=None, **kwargs):
        if db_field.name in self.filter_horizontal:
            kwargs["widget"] = SortedFilteredSelectMultiple()
        return super().formfield_for_manytomany(db_field, request, **kwargs)

    # Method to display a list of subjects in the admin list view
    def subjects_list(self, obj):
        return ", ".join([subject.name for subject in obj.subjects.all()])

    subjects_list.short_description = "subjects"


# Register FeedbackSubject model with ImportExportMixin
@admin.register(FeedbackSubject)
class FeedbackSubjectAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = ("id", "name")
    list_display_links = list_display
    search_fields = ("name",)


# Define an inline admin for Guess model
class GuessInline(admin.TabularInline):
    model = Guess
    extra = 0
    max_num = 0
    can_delete = False
    exclude = ("id", "order")


# Register UserActivity model with AnalyticsMixin, ImportExportMixin, and custom admin options
@admin.register(UserActivity)
class UserActivityAdmin(AnalyticsMixin, ImportExportMixin, admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "start_time",
        "archive_id",
        "total_time",
        "guessed_movies_count_display",
        "winner_display",
        "is_replayed",
        "is_shared",
    )
    list_display_links = list_display
    search_fields = ("user__uuid",)
    readonly_fields = ("guessed_movies_count_display", "total_time", "winner_display")
    inlines = [GuessInline]
    ordering = ("-start_time",)
    resource_class = UserActivityResource
    export_form_class = SelectiveExportForm

    # Method to pass additional kwargs to the export resource
    def get_export_resource_kwargs(self, request, *args, **kwargs):
        export_form = kwargs["export_form"]
        if export_form:
            return {
                "start_date": export_form.cleaned_data.get("start_date"),
                "end_date": export_form.cleaned_data.get("end_date"),
            }
        return {}

    # Method to determine readonly fields dynamically
    def get_readonly_fields(self, request, obj=None):
        readonly_fields = [field.name for field in self.model._meta.fields]
        readonly_fields.remove("id")
        return readonly_fields + list(self.readonly_fields)

    # Prevent adding new UserActivity instances
    def has_add_permission(self, request):
        return False

    # Prevent changing existing UserActivity instances
    def has_change_permission(self, request, obj=None):
        return False

    # Method to display winner in a readable format
    def winner_display(self, obj):
        return obj.winner

    # Method to display guessed movies count in a readable format
    def guessed_movies_count_display(self, obj):
        return obj.guessed_movies_count

    winner_display.boolean = True
    winner_display.short_description = "winner"
    guessed_movies_count_display.short_description = "guess count"


# Register User model with ImportExportMixin and prevent any modifications
@admin.register(User)
class UserAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = ("id", "uuid", "email")
    list_display_links = list_display
    search_fields = ("uuid", "email")

    # Prevent adding new User instances
    def has_add_permission(self, request):
        return False

    # Prevent changing existing User instances
    def has_change_permission(self, request, obj=None):
        return False

    # Prevent deleting User instances
    def has_delete_permission(self, request, obj=None):
        return False
