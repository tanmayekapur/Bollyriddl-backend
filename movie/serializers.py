from rest_framework import serializers, exceptions
from .models import Movie, Contact, Feedback, FeedbackSubject, User, Guess, UserActivity


# Serializer for the Movie model
class MovieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Movie
        fields = (
            "__all__"  # Includes all fields of the Movie model in the serialization
        )
        exclude = None  # Excludes no fields
        depth = 1  # Sets the depth of relationships to 1

    def __init__(self, *args, **kwargs):
        # Customize serializer fields based on the view action
        context = kwargs.get("context", {})
        view = context.get("view", None)

        if view is not None:
            if view.action == "list":
                self.Meta.fields = ("id", "name")  # Limit fields for list action
                self.Meta.exclude = None

            elif view.action == "retrieve":
                raise exceptions.NotFound(
                    "Not found.", "not_found"
                )  # Raise 404 for retrieve action
            elif view.action == "get_mystery_movie":
                self.Meta.fields = None
                self.Meta.exclude = (
                    "imdb_id",
                )  # Exclude IMDb ID for get_mystery_movie action
                self.Meta.depth = 0  # Set depth to 0 for get_mystery_movie action
            elif view.action == "match_mystery_movie":
                self.Meta.fields = None
                self.Meta.exclude = (
                    "imdb_id",
                )  # Exclude IMDb ID for match_mystery_movie action
                self.Meta.depth = 1  # Set depth to 1 for match_mystery_movie action
        super().__init__(*args, **kwargs)


# Serializer for the Contact model
class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = (
            "__all__"  # Includes all fields of the Contact model in the serialization
        )


# Serializer for the Feedback model
class FeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = (
            "__all__"  # Includes all fields of the Feedback model in the serialization
        )


# Serializer for the FeedbackSubject model
class FeedbackSubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeedbackSubject
        fields = "__all__"  # Includes all fields of the FeedbackSubject model in the serialization


# Serializer for the Guess model
class GuessSerializer(serializers.ModelSerializer):
    class Meta:
        model = Guess
        exclude = [
            "user_activity"
        ]  # Excludes the user_activity field from serialization


# Serializer for the User model
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"  # Includes all fields of the User model in the serialization


# Serializer for the UserActivity model
class UserActivitySerializer(serializers.ModelSerializer):
    # Nested serializer for guessed_movies field
    guessed_movies = GuessSerializer(
        many=True, required=False, allow_empty=True, write_only=True
    )

    class Meta:
        model = UserActivity
        fields = "__all__"  # Includes all fields of the UserActivity model in the serialization

    # Custom validation method for start_time and end_time
    def validate(self, attrs):
        start_time = attrs.get("start_time")
        end_time = attrs.get("end_time")
        if start_time and end_time:
            if end_time < start_time:
                raise exceptions.ValidationError("End time cannot be before start time")

            if start_time.date() != end_time.date():
                raise exceptions.ValidationError(
                    "Start and end time must be on the same date"
                )

        return super().validate(attrs)

    # Custom representation method to modify serialization output
    def to_representation(self, instance):
        repr = super().to_representation(instance)
        repr["total_time"] = str(instance.total_time)
        repr["guessed_movies_count"] = instance.guessed_movies_count
        repr["guessed_movies"] = []
        guessed_movies = (
            Guess.objects.filter(user_activity=instance)
            .prefetch_related("movie")
            .order_by("order")
        )
        for guessed_movie in guessed_movies.all():
            repr["guessed_movies"].append(
                {
                    "movie": guessed_movie.movie.id,
                    "time_taken": str(guessed_movie.time_taken),
                    "order": guessed_movie.order,
                }
            )
        return repr

    # Custom create method to handle nested serialization
    def create(self, validated_data):
        guessed_movies = None
        if "guessed_movies" in validated_data:
            guessed_movies = validated_data.pop("guessed_movies")

        user_activity = UserActivity.objects.create(**validated_data)

        if guessed_movies is not None:
            for order, guessed_movie in enumerate(guessed_movies):
                Guess.objects.create(
                    user_activity=user_activity, order=order, **guessed_movie
                )
        return user_activity

    # Custom update method to handle nested serialization
    def update(self, instance, validated_data):
        if "guessed_movies" in validated_data:
            guessed_movies = validated_data.pop("guessed_movies")
            for order, guessed_movie in enumerate(guessed_movies):
                Guess.objects.update_or_create(
                    user_activity=instance, order=order, defaults=guessed_movie
                )
        return super().update(instance, validated_data)
