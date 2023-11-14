from rest_framework import viewsets, permissions, exceptions
from rest_framework.response import Response
from rest_framework.decorators import action
import datetime

from .serializers import MovieSerializer, ContactSerializer
from .models import Movie, Archive, Contact

# Create your views here.


class MovieViewSet(viewsets.ModelViewSet):
    queryset = Movie.objects.all()
    serializer_class = MovieSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    http_method_names = ["get", "head"]
    search_fields = ["name"]
    ordering_fields = ["name"]

    def get_object(self):
        raise exceptions.NotFound("Not found.", "not_found")

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        response.data = [data["name"] for data in response.data]
        return response

    @action(
        detail=False,
        methods=["get"],
        url_path="match-mystery-movie",
        name="Match Mystery Movie",
    )
    def match_mystery_movie(self, request):
        movie_name = request.query_params.get("name")
        date = request.query_params.get("date")

        validation_errors = {}

        if not movie_name:
            validation_errors["name"] = ["This field may not be blank."]

        if not date:
            validation_errors["date"] = ["This field may not be blank."]

        if validation_errors:
            raise exceptions.ValidationError(validation_errors, "blank")

        try:
            datetime.datetime.strptime(date, "%Y-%m-%d")
        except Exception:
            validation_errors["date"] = [
                f"'{date}' value has an invalid date format. It must be in YYYY-MM-DD format."
            ]

        if validation_errors:
            raise exceptions.ValidationError(validation_errors, "invalid")

        try:
            guessed_movie = Movie.objects.get(name__iexact=movie_name)
        except Exception:
            validation_errors["name"] = [
                f"Movie with name '{movie_name}' does not exists."
            ]

        try:
            mystery_movie = Archive.objects.get(date=date)
        except Exception:
            validation_errors["date"] = [
                f"Mystery movie on date '{date}' does not exists."
            ]

        if validation_errors:
            raise exceptions.NotFound(validation_errors, "not_found")

        data = self.get_serializer(guessed_movie).data

        if guessed_movie == mystery_movie.movie:
            data["message"] = "Movie matched."
            return Response(data, status=200)

        else:
            mystery_movie = mystery_movie.movie
            data["message"] = "Movie not matched."
            data.pop("name")

            if guessed_movie.year != mystery_movie.year:
                data.pop("year")

            if guessed_movie.director != mystery_movie.director:
                data.pop("director")

            if guessed_movie.production_house != mystery_movie.production_house:
                data.pop("production_house")

            common_genres = mystery_movie.genres.all().intersection(
                guessed_movie.genres.all()
            )
            if common_genres.exists():
                data["genres"] = [genre.name for genre in common_genres]
            else:
                data.pop("genres")

            common_cast = mystery_movie.cast.all().intersection(
                guessed_movie.cast.all()
            )
            if common_cast.exists():
                data["cast"] = [cast.name for cast in common_cast]
            else:
                data.pop("cast")

            common_writers = mystery_movie.writers.all().intersection(
                guessed_movie.writers.all()
            )
            if common_writers.exists():
                data["writers"] = [writers.name for writers in common_writers]
            else:
                data.pop("writers")

            common_music_directors = mystery_movie.music_directors.all().intersection(
                guessed_movie.music_directors.all()
            )
            if common_music_directors.exists():
                data["music_directors"] = [
                    music_directors.name for music_directors in common_music_directors
                ]
            else:
                data.pop("music_directors")

            return Response(data, status=200)


class ContactViewSet(viewsets.ModelViewSet):
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer
    permission_classes = [permissions.AllowAny]
    http_method_names = ["post", "head"]
