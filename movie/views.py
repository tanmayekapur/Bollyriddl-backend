from rest_framework import viewsets, permissions, exceptions
from rest_framework.response import Response
from rest_framework.decorators import action
import datetime

from .serializers import (
    MovieSerializer,
    ContactSerializer,
    FeedbackSerializer,
    FeedbackSubjectSerializer,
)
from .models import Movie, Archive, Contact, Feedback, FeedbackSubject

# Create your views here.


class MovieViewSet(viewsets.ModelViewSet):
    queryset = Movie.objects.all()
    serializer_class = MovieSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    http_method_names = ["get", "head"]
    search_fields = ["name"]
    ordering_fields = ["name"]

    def get_object(self):
        if self.action == "get_hint":
            self.queryset = Archive.objects.all()

        return super().get_object()

    @action(
        detail=False,
        methods=["get"],
        url_path="get-mystery-movie",
        name="Get Mystery Movie",
    )
    def get_mystery_movie(self, request):
        today = datetime.date.today()
        date = request.query_params.get("date")

        if date:
            try:
                date = datetime.datetime.strptime(date, "%Y-%m-%d").date()
            except Exception:
                raise exceptions.ValidationError(
                    {
                        "date": [
                            f"'{date}' value has an invalid date format. It must be in YYYY-MM-DD format."
                        ]
                    },
                    "invalid",
                )
        else:
            date = today

        if Archive.objects.filter(date=date).exists():
            mystery_movie = Archive.objects.get(date=date)
            data = self.get_serializer(mystery_movie.movie).data
            data["id"] = mystery_movie.id
            return Response(data, status=200)

        else:
            raise exceptions.NotFound("Not found.", "not_found")

    @action(
        detail=True,
        methods=["get"],
        url_path="get-hint",
        name="Get Hint",
    )
    def get_hint(self, request, *args, **kwargs):
        movie = self.get_object().movie
        id = request.query_params.get("id")
        key = request.query_params.get("key")
        keys = [
            "genres",
            "cast",
            "writers",
            "directors",
            "music_directors",
            "production_houses",
        ]

        validation_errors = {}

        if not id:
            validation_errors["id"] = ["This field may not be blank."]

        if not key:
            validation_errors["key"] = ["This field may not be blank."]

        if validation_errors:
            raise exceptions.ValidationError(validation_errors, "blank")

        try:
            id = int(id)
        except Exception:
            validation_errors["id"] = ["'id' value must be an integer."]

        if key not in keys:
            validation_errors["key"] = [f"'key' value must be one of: {keys}"]

        if validation_errors:
            raise exceptions.ValidationError(validation_errors, "invalid")

        if getattr(movie, key).filter(id=id).exists():
            value = getattr(movie, key).get(id=id)
            return Response(value.name, status=200)
        else:
            raise exceptions.NotFound("Not found.", "not_found")

    @action(
        detail=True,
        methods=["get"],
        url_path="match-mystery-movie",
        name="Match Mystery Movie",
    )
    def match_mystery_movie(self, request, *args, **kwargs):
        date = request.query_params.get("date")
        validation_errors = {}

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
            mystery_movie = Archive.objects.get(date=date)
        except Exception:
            validation_errors["date"] = [
                f"Mystery movie on date '{date}' does not exists."
            ]

        if validation_errors:
            raise exceptions.NotFound(validation_errors, "not_found")

        guessed_movie = self.get_object()
        data = self.get_serializer(guessed_movie).data

        if guessed_movie == mystery_movie.movie:
            data["message"] = "Movie matched."
            return Response(data, status=200)

        else:
            mystery_movie_data = self.get_serializer(mystery_movie.movie).data
            data["message"] = "Movie not matched."
            common_data = {}

            for key, value in data.items():
                if isinstance(value, list):
                    common_data[key] = [
                        item
                        for item in value
                        if item in mystery_movie_data.get(key, [])
                    ]
                else:
                    common_data[key] = value

            return Response(common_data, status=200)


class ContactViewSet(viewsets.ModelViewSet):
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer
    permission_classes = [permissions.AllowAny]
    http_method_names = ["post", "head"]


class FeedbackViewSet(viewsets.ModelViewSet):
    queryset = Feedback.objects.all()
    serializer_class = FeedbackSerializer
    permission_classes = [permissions.AllowAny]
    http_method_names = ["post", "head"]


class FeedbackSubjectViewSet(viewsets.ModelViewSet):
    queryset = FeedbackSubject.objects.all()
    serializer_class = FeedbackSubjectSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    http_method_names = ["get", "head"]

    def get_object(self):
        raise exceptions.NotFound("Not found.", "not_found")
