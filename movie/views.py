from rest_framework import viewsets, permissions, exceptions
from rest_framework.filters import SearchFilter
from rest_framework.response import Response
from rest_framework.decorators import action
from django.utils import timezone

from .filters import PriorizedSearchFilter  # Importing custom filter
from .serializers import (  # Importing serializers
    MovieSerializer,
    ContactSerializer,
    FeedbackSerializer,
    FeedbackSubjectSerializer,
    UserSerializer,
    UserActivitySerializer,
)
from .models import (  # Importing models
    Movie,
    Archive,
    Contact,
    Feedback,
    FeedbackSubject,
    User,
    UserActivity,
)

# Create your views here.


# ViewSet for handling Movie model operations
class MovieViewSet(viewsets.ModelViewSet):
    # Queryset for retrieving all Movie objects
    queryset = Movie.objects.all()
    # Serializer class to use for Movie objects
    serializer_class = MovieSerializer
    # Permission classes to check for Movie operations
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    # HTTP methods allowed for Movie operations
    http_method_names = ["get", "head"]
    # Default size for search results
    search_size = 10
    # Fields to search for Movie objects
    search_fields = ["^name", "name"]
    # Fields to order Movie objects
    ordering_fields = ["name"]

    # Custom method to override default behavior for retrieving a single object
    def get_object(self):
        # If the action is 'get_hint', query Archive objects instead of Movie objects
        if self.action == "get_hint":
            self.queryset = Archive.objects.all()

        return super().get_object()

    # Custom method to filter queryset based on action
    def filter_queryset(self, queryset):
        filter_backends = []

        # Modify filter backends based on action
        for filter_backend in self.filter_backends:
            if filter_backend is SearchFilter:
                filter_backends.append(PriorizedSearchFilter)
                continue
            filter_backends.append(filter_backend)

        self.filter_backends = filter_backends
        queryset = super().filter_queryset(queryset)

        # Limit queryset size for 'list' action
        if self.action == "list":
            return queryset[: self.search_size]

        return queryset

    # Custom action to get mystery movie for a given date
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

        # Parse and validate date
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

        # Check if mystery movie exists for given date
        if Archive.objects.filter(date=date).exists() and date <= today:
            mystery_movie = Archive.objects.get(date=date)
            data = self.get_serializer(mystery_movie.movie).data
            data["id"] = mystery_movie.id
            data["movie_id"] = mystery_movie.movie.id
            data["today_archive_id"] = mystery_movie.archive_id
            return Response(data, status=200)

        else:
            raise exceptions.NotFound("Not found.", "not_found")

    # Custom action to get hint for a movie attribute
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

        # Validate query parameters
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

        # Retrieve value for the specified key
        if getattr(movie, key).filter(id=id).exists():
            value = getattr(movie, key).get(id=id)
            return Response(value.name, status=200)
        else:
            raise exceptions.NotFound("Not found.", "not_found")

    # Custom action to match guessed movie with mystery movie for a given date
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

        # Validate query parameters
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

        # Check if guessed movie matches mystery movie
        if guessed_movie == mystery_movie.movie:
            data["message"] = "Movie matched."
            data["matched"] = True
            return Response(data, status=200)

        else:
            mystery_movie_data = self.get_serializer(mystery_movie.movie).data
            data["message"] = "Movie not matched."
            data["matched"] = False
            common_data = {}

            # Find common data between guessed and mystery movies
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


# ViewSet for handling Contact model operations
class ContactViewSet(viewsets.ModelViewSet):
    queryset = Contact.objects.all()  # Queryset for retrieving all Contact objects
    serializer_class = ContactSerializer  # Serializer class for Contact objects
    permission_classes = [permissions.AllowAny]  # Permissions for Contact operations
    http_method_names = ["post", "head"]  # HTTP methods allowed for Contact operations


# ViewSet for handling Feedback model operations
class FeedbackViewSet(viewsets.ModelViewSet):
    queryset = Feedback.objects.all()  # Queryset for retrieving all Feedback objects
    serializer_class = FeedbackSerializer  # Serializer class for Feedback objects
    permission_classes = [permissions.AllowAny]  # Permissions for Feedback operations
    http_method_names = ["post", "head"]  # HTTP methods allowed for Feedback operations


# ViewSet for handling FeedbackSubject model operations
class FeedbackSubjectViewSet(viewsets.ModelViewSet):
    queryset = (
        FeedbackSubject.objects.all()
    )  # Queryset for retrieving all FeedbackSubject objects
    serializer_class = (
        FeedbackSubjectSerializer  # Serializer class for FeedbackSubject objects
    )
    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly
    ]  # Permissions for FeedbackSubject operations
    http_method_names = [
        "get",
        "head",
    ]  # HTTP methods allowed for FeedbackSubject operations

    # Custom method to raise NotFound exception when trying to retrieve an object
    def get_object(self):
        raise exceptions.NotFound("Not found.", "not_found")


# ViewSet for handling User model operations
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()  # Queryset for retrieving all User objects
    serializer_class = UserSerializer  # Serializer class for User objects
    permission_classes = [permissions.AllowAny]  # Permissions for User operations
    http_method_names = [
        "get",
        "post",
        "head",
    ]  # HTTP methods allowed for User operations

    # Custom method to raise NotFound exception when trying to retrieve queryset
    def get_queryset(self):
        raise exceptions.NotFound("Not found.", "not_found")

    # Custom method to raise NotFound exception when trying to retrieve an object
    def get_object(self):
        raise exceptions.NotFound("Not found.", "not_found")

    # Custom action to create a new user
    @action(
        detail=False,
        methods=["get"],
        url_path="create-user",
        name="Create User",
    )
    def create_user(self, request):
        user = User.objects.create()  # Create a new User object
        data = self.get_serializer(user).data  # Serialize User object data
        return Response(data, status=200)  # Return serialized data with success status

    # Custom action to save user email
    @action(
        detail=False,
        methods=["post"],
        url_path="save-email",
        name="Save Email",
    )
    def save_email(self, request):
        uuid = request.data.get("uuid", None)  # Get UUID from request data
        email = request.data.get("email", None)  # Get email from request data

        # Validate email field
        if email == None:
            raise exceptions.ValidationError(
                {"email": ["This field may not be blank."]}, "blank"
            )

        serializer = self.get_serializer(data=request.data)  # Get serializer instance
        serializer.is_valid(raise_exception=True)  # Validate serializer data

        # Update or create user email based on UUID
        if uuid != None:
            user = User.objects.filter(uuid=uuid).first()  # Get user by UUID
            if user is None:
                raise exceptions.NotFound("Not found.", "not_found")
            user.email = email  # Update user email
            user.save()  # Save user
        else:
            user = User.objects.create(email=email)  # Create new user with email

        data = self.get_serializer(user).data  # Serialize user data
        return Response(data, status=200)  # Return serialized data with success status


# ViewSet for handling UserActivity model operations
class UserActivityViewSet(viewsets.ModelViewSet):
    queryset = (
        UserActivity.objects.all()
    )  # Queryset for retrieving all UserActivity objects
    serializer_class = (
        UserActivitySerializer  # Serializer class for UserActivity objects
    )
    permission_classes = [
        permissions.AllowAny
    ]  # Permissions for UserActivity operations
    http_method_names = [
        "post",
        "patch",
        "head",
    ]  # HTTP methods allowed for UserActivity operations
