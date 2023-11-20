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

    @action(
        detail=False,
        methods=["get"],
        url_path="get-mystery-movie",
        name="Get Mystery Movie",
    )
    def get_mystery_movie(self, request):
        today = datetime.date.today()
        if Archive.objects.filter(date=today).exists():
            mystery_movie = Archive.objects.get(date=today)
            data = self.get_serializer(mystery_movie.movie).data
            data["id"] = mystery_movie.id
            return Response(data, status=200)

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
