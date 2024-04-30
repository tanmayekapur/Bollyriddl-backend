from import_export import resources, fields
from .mixins import RelatedResourceMixin
from .models import Movie, UserActivity, Archive
from django.utils import timezone


class MovieResource(RelatedResourceMixin):
    """
    Resource class for Movie model.
    """

    class Meta:
        model = Movie  # Specifies the model this resource is associated with

    def before_import_row(self, row, **kwargs):
        """
        Override before_import_row to handle unique constraint violations and preprocess data.
        """
        name = row.get("name", None)  # Extracts the 'name' field from the row
        imdb_id = row.get("imdb_id", None)  # Extracts the 'imdb_id' field from the row

        # Checks if a movie with the same name exists in the database
        if name:
            if Movie.objects.filter(name=name).exists():
                # If a movie with the same name exists, sets the 'id' field of the row to the existing movie's id
                row["id"] = Movie.objects.get(name=name).id

        # Checks if a movie with the same IMDb ID exists in the database
        if imdb_id:
            if Movie.objects.filter(imdb_id=imdb_id).exists():
                # If a movie with the same IMDb ID exists, sets the 'id' field of the row to the existing movie's id
                row["id"] = Movie.objects.get(imdb_id=imdb_id).id

        # Preprocesses the 'genres' field, converting each value to title case
        if "genres" in row:
            row["genres"] = [string.title() for string in row.get("genres", [])]
        # Preprocesses the 'cast' field, converting each value to title case
        if "cast" in row:
            row["cast"] = [string.title() for string in row.get("cast", [])]
        # Preprocesses the 'writers' field, converting each value to title case
        if "writers" in row:
            row["writers"] = [string.title() for string in row.get("writers", [])]
        # Preprocesses the 'directors' field, converting each value to title case
        if "directors" in row:
            row["directors"] = [string.title() for string in row.get("directors", [])]
        # Preprocesses the 'music_directors' field, converting each value to title case
        if "music_directors" in row:
            row["music_directors"] = [
                string.title() for string in row.get("music_directors", [])
            ]
        # Preprocesses the 'production_houses' field, converting each value to title case
        if "production_houses" in row:
            row["production_houses"] = [
                string.title() for string in row.get("production_houses", [])
            ]

        super().before_import_row(
            row, **kwargs
        )  # Calls the parent class's before_import_row method


class UserActivityResource(resources.ModelResource):
    """
    Resource class for UserActivity model.
    """

    # Custom fields to map model fields to specific column names in the exported file
    id = fields.Field("id", column_name="session_id")
    user_id = fields.Field(column_name="user_id")
    start_date = fields.Field(column_name="start_date")
    end_date = fields.Field(column_name="end_date")
    total_time = fields.Field("total_time", column_name="duration")
    winner = fields.Field("winner", column_name="winner_status")
    is_replayed = fields.Field("is_replayed", column_name="replayed_status")
    is_shared = fields.Field("is_shared", column_name="shared_status")
    lifelines_used = fields.Field(column_name="lifelines_used")
    game_number = fields.Field(column_name="game_number")
    archive_id = fields.Field(column_name="archive_id")
    guess_count = fields.Field("guessed_movies_count", column_name="guess_count")
    guessed_movies = fields.Field(column_name="guessed_movies")
    time_taken = fields.Field(column_name="time_taken")

    class Meta:
        model = UserActivity  # Specifies the model this resource is associated with

    def __init__(self, **kwargs):
        super().__init__()
        self.filter_start_date = kwargs.get(
            "start_date"
        )  # Initializes start_date filter
        self.filter_end_date = kwargs.get("end_date")  # Initializes end_date filter

    def filter_export(self, queryset, *args, **kwargs):
        """
        Custom method to filter the queryset based on start_date and end_date filters.
        """
        # Orders the queryset by start_time in descending order
        queryset = queryset.order_by("-start_time")
        # Filters the queryset based on start_date and end_date if provided
        if self.filter_start_date and self.filter_end_date:
            return queryset.filter(
                start_time__date__range=(self.filter_start_date, self.filter_end_date)
            )
        return queryset

    # Custom methods to dehydrate (convert) model fields before exporting
    def dehydrate_user_id(self, obj):
        return obj.user.uuid  # Dehydrates user_id field to UUID format

    def dehydrate_game_number(self, obj):
        return obj.archive.id  # Dehydrates game_number field to archive id

    def dehydrate_archive_id(self, obj):
        return (
            obj.archive.archive_id
        )  # Dehydrates archive_id field to custom archive_id

    def dehydrate_start_date(self, obj):
        """
        Dehydrates start_time field to local timezone.
        """
        if obj.start_time is None:
            return None
        return timezone.localtime(obj.start_time)

    def dehydrate_end_date(self, obj):
        """
        Dehydrates end_time field to local timezone.
        """
        if obj.end_time is None:
            return None
        return timezone.localtime(obj.end_time)

    def dehydrate_lifelines_used(self, obj):
        """
        Dehydrates lifelines_used field to comma-separated string.
        """
        lifelines_used = obj.lifelines_used
        lifelines_used = list(map(lambda x: str(x), lifelines_used))
        return ", ".join(lifelines_used)

    def dehydrate_guessed_movies(self, obj):
        """
        Dehydrates guessed_movies field to comma-separated string.
        """
        guessed_movies = list(obj.guessed_movies.all().values_list("id", flat=True))
        guessed_movies = list(map(lambda x: str(x), guessed_movies))
        return ", ".join(guessed_movies)

    def dehydrate_time_taken(self, obj):
        """
        Dehydrates time_taken field to comma-separated string.
        """
        guesses = list(
            obj.guess_set.all().order_by("order").values_list("time_taken", flat=True)
        )
        guesses = list(map(lambda x: str(x), guesses))
        return ", ".join(guesses)

    def get_export_order(self):
        """
        Specifies the order of fields in the exported file.
        """
        return (
            "id",
            "user_id",
            "start_date",
            "end_date",
            "game_number",
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

    # Custom field to map model field to a specific column name in the exported file
    archive_id = fields.Field(column_name="archive_id")

    class Meta:
        model = Archive  # Specifies the model this resource is associated with

    def dehydrate_archive_id(self, obj):
        """
        Custom method to dehydrate (convert) the archive_id field before exporting.
        """
        return obj.archive_id  # Dehydrates archive_id field to custom archive_id
