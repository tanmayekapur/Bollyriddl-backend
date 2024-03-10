from import_export import resources, fields
from .mixins import RelatedResourceMixin
from .models import Movie, UserActivity


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

    id = fields.Field(column_name="session_id")
    user_id = fields.Field(column_name="user_id")
    start_date = fields.Field(column_name="date")
    start_time = fields.Field(column_name="time")
    total_time = fields.Field(column_name="duration")
    winner = fields.Field(column_name="winner_status")
    archive_id = fields.Field(column_name="game_number")
    guessed_movies = fields.Field(column_name="guessed_movies")
    guess_count = fields.Field(column_name="guess_count")

    class Meta:
        model = UserActivity

    def dehydrate_id(self, obj):
        return obj.id

    def dehydrate_user_id(self, obj):
        return obj.user.uuid

    def dehydrate_archive_id(self, obj):
        return obj.archive.id

    def dehydrate_total_time(self, obj):
        return obj.total_time

    def dehydrate_start_date(self, obj):
        return obj.start_time.date()

    def dehydrate_start_time(self, obj):
        return obj.start_time.time()

    def dehydrate_winner(self, obj):
        return obj.winner

    def dehydrate_guess_count(self, obj):
        return obj.guessed_movies_count

    def dehydrate_guessed_movies(self, obj):
        guessed_movies = list(obj.guessed_movies.all().values_list("id", flat=True))
        guessed_movies = list(map(lambda x: str(x), guessed_movies))
        return ", ".join(guessed_movies)

    def get_export_order(self):
        return (
            "id",
            "user_id",
            "start_date",
            "start_time",
            "archive_id",
            "total_time",
            "guess_count",
            "winner",
            "guessed_movies",
        )
