from import_export import resources, fields
from .mixins import RelatedResourceMixin
from .models import Movie, UserActivity, Archive
from django.utils import timezone


class MovieResource(RelatedResourceMixin):
    """
    Resource class for Movie model.
    """

    class Meta:
        model = Movie

    def before_import_row(self, row, **kwargs):
        """
        Override before_import_row to handle unique constraint violations.
        """
        name = row.get("name", None)
        imdb_id = row.get("imdb_id", None)
        if name:
            if Movie.objects.filter(name=name).exists():
                row["id"] = Movie.objects.get(name=name).id

        if imdb_id:
            if Movie.objects.filter(imdb_id=imdb_id).exists():
                row["id"] = Movie.objects.get(imdb_id=imdb_id).id

        super().before_import_row(row, **kwargs)


class UserActivityResource(resources.ModelResource):
    """
    Resource class for UserActivity model.
    """

    id = fields.Field("id", column_name="session_id")
    user_id = fields.Field(column_name="user_id")
    start_date = fields.Field(column_name="start_date")
    end_date = fields.Field(column_name="end_date")
    total_time = fields.Field("total_time", column_name="duration")
    winner = fields.Field("winner", column_name="winner_status")
    is_replayed = fields.Field("is_replayed", column_name="replayed_status")
    is_shared = fields.Field("is_shared", column_name="shared_status")
    lifelines_used = fields.Field(column_name="lifelines_used")
    archive_id = fields.Field(column_name="game_number")
    guess_count = fields.Field("guessed_movies_count", column_name="guess_count")
    guessed_movies = fields.Field(column_name="guessed_movies")
    time_taken = fields.Field(column_name="time_taken")

    class Meta:
        model = UserActivity

    def __init__(self, **kwargs):
        super().__init__()
        self.filter_start_date = kwargs.get("start_date")
        self.filter_end_date = kwargs.get("end_date")

    def filter_export(self, queryset, *args, **kwargs):
        queryset = queryset.order_by("-start_time")
        if self.filter_start_date and self.filter_end_date:
            return queryset.filter(
                start_time__date__range=(self.filter_start_date, self.filter_end_date)
            )
        return queryset

    def dehydrate_user_id(self, obj):
        return obj.user.uuid

    def dehydrate_archive_id(self, obj):
        return obj.archive.id

    def dehydrate_start_date(self, obj):
        if obj.start_time is None:
            return None
        return timezone.localtime(obj.start_time)

    def dehydrate_end_date(self, obj):
        if obj.end_time is None:
            return None
        return timezone.localtime(obj.end_time)

    def dehydrate_lifelines_used(self, obj):
        lifelines_used = obj.lifelines_used
        lifelines_used = list(map(lambda x: str(x), lifelines_used))
        return ", ".join(lifelines_used)

    def dehydrate_guessed_movies(self, obj):
        guessed_movies = list(obj.guessed_movies.all().values_list("id", flat=True))
        guessed_movies = list(map(lambda x: str(x), guessed_movies))
        return ", ".join(guessed_movies)

    def dehydrate_time_taken(self, obj):
        guesses = list(
            obj.guess_set.all().order_by("order").values_list("time_taken", flat=True)
        )
        guesses = list(map(lambda x: str(x), guesses))
        return ", ".join(guesses)

    def get_export_order(self):
        return (
            "id",
            "user_id",
            "start_date",
            "end_date",
            "archive_id",
            "total_time",
            "guess_count",
            "winner",
            "is_replayed",
            "is_shared",
            "lifelines_used",
            "guessed_movies",
            "time_taken",
        )


class ArchiveResource(resources.ModelResource):
    """
    Resource class for Archive model.
    """

    archive_id = fields.Field(column_name="archive_id")

    class Meta:
        model = Archive

    def dehydrate_archive_id(self, obj):
        return obj.archive_id
