from rest_framework import viewsets, permissions, exceptions
from rest_framework.filters import SearchFilter
from rest_framework.response import Response
from rest_framework.decorators import action
from django.utils import timezone

from .filters import PriorizedSearchFilter
from .serializers import (
    MovieSerializer,
    ContactSerializer,
    FeedbackSerializer,
    FeedbackSubjectSerializer,
    UserSerializer,
    UserActivitySerializer,
)
from .models import (
    Movie,
    Archive,
    Contact,
    Feedback,
    FeedbackSubject,
    User,
    UserActivity,
)

# Create your views here.


class MovieViewSet(viewsets.ModelViewSet):
    queryset = Movie.objects.all()
    serializer_class = MovieSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    http_method_names = ["get", "head"]
    search_size = 10
    search_fields = ["^name", "name"]
    ordering_fields = ["name"]

    def get_object(self):
        if self.action == "get_hint":
            self.queryset = Archive.objects.all()

        return super().get_object()

    def filter_queryset(self, queryset):
        filter_backends = []

        for filter_backend in self.filter_backends:
            if filter_backend is SearchFilter:
                filter_backends.append(PriorizedSearchFilter)
                continue
            filter_backends.append(filter_backend)

        self.filter_backends = filter_backends
        queryset = super().filter_queryset(queryset)

        if self.action == "list":
            return queryset[: self.search_size]

        return queryset

    @action(
        detail=False,
        methods=["get"],
        url_path="get-mystery-movie",
        name="Get Mystery Movie",
    )
    def get_mystery_movie(self, request):
        today = timezone.localtime().date()
        date = request.query_params.get("date")
        iso_format = "%Y-%m-%dT%H:%M:%S.%fZ"

        if date:
            try:
                tz = timezone.get_current_timezone()
                date = timezone.datetime.strptime(date, iso_format)
                date = timezone.make_aware(date, timezone=timezone.utc)
                date = date.astimezone(tz).date()
            except Exception:
                raise exceptions.ValidationError(
                    {
                        "date": [
                            f"'{date}' value has an invalid date format. It must be in ISO format."
                        ]
                    },
                    "invalid",
                )
        else:
            date = today

        if Archive.objects.filter(date=date).exists() and date <= today:
            mystery_movie = Archive.objects.get(date=date)
            data = self.get_serializer(mystery_movie.movie).data
            data["id"] = mystery_movie.id
            data["movie_id"] = mystery_movie.movie.id
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
        iso_format = "%Y-%m-%dT%H:%M:%S.%fZ"
        validation_errors = {}

        if not date:
            validation_errors["date"] = ["This field may not be blank."]

        if validation_errors:
            raise exceptions.ValidationError(validation_errors, "blank")

        try:
            tz = timezone.get_current_timezone()
            date = timezone.datetime.strptime(date, iso_format)
            date = timezone.make_aware(date, timezone=timezone.utc)
            date = date.astimezone(tz).date()
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
            data["matched"] = True
            return Response(data, status=200)

        else:
            mystery_movie_data = self.get_serializer(mystery_movie.movie).data
            data["message"] = "Movie not matched."
            data["matched"] = False
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


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]
    http_method_names = ["get", "head"]

    def get_queryset(self):
        raise exceptions.NotFound("Not found.", "not_found")

    def get_object(self):
        raise exceptions.NotFound("Not found.", "not_found")

    @action(
        detail=False,
        methods=["get"],
        url_path="create-user",
        name="Create User",
    )
    def create_user(self, request):
        user = User.objects.create()
        data = self.get_serializer(user).data
        return Response(data, status=200)

    @action(
        detail=False,
        methods=["post"],
        url_path="save-email",
        name="Save Email",
    )
    def save_email(self, request):
        uuid = request.data.get("uuid", None)
        email = request.data.get("email", None)

        if email == None:
            raise exceptions.ValidationError(
                {"email": ["This field may not be blank."]}, "blank"
            )

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if uuid != None:
            user = User.objects.filter(uuid=uuid)
            if not user.exists():
                raise exceptions.NotFound("Not found.", "not_found")
            user = user.first()
            user.email = email
            user.save()
        else:
            user = User.objects.create(email=email)

        data = self.get_serializer(user).data
        return Response(data, status=200)


class UserActivityViewSet(viewsets.ModelViewSet):
    queryset = UserActivity.objects.all()
    serializer_class = UserActivitySerializer
    permission_classes = [permissions.AllowAny]
    http_method_names = ["post", "patch", "head"]
