from rest_framework import serializers, exceptions
from .models import Movie, Contact, Feedback, FeedbackSubject, User, Guess, UserActivity


class MovieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Movie
        fields = "__all__"
        exclude = None
        depth = 1

    def __init__(self, *args, **kwargs):
        context = kwargs.get("context", {})
        view = context.get("view", None)

        if view is not None:
            if view.action == "list":
                self.Meta.fields = ("id", "name")
                self.Meta.exclude = None

            elif view.action == "retrieve":
                raise exceptions.NotFound("Not found.", "not_found")

            elif view.action == "get_mystery_movie":
                self.Meta.fields = None
                self.Meta.exclude = ("imdb_id",)
                self.Meta.depth = 0

            elif view.action == "match_mystery_movie":
                self.Meta.fields = None
                self.Meta.exclude = ("imdb_id",)
                self.Meta.depth = 1

        super().__init__(*args, **kwargs)


class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = "__all__"


class FeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = "__all__"


class FeedbackSubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeedbackSubject
        fields = "__all__"


class GuessSerializer(serializers.ModelSerializer):
    class Meta:
        model = Guess
        exclude = ["user_activity"]


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"


class UserActivitySerializer(serializers.ModelSerializer):
    guessed_movies = GuessSerializer(
        many=True, required=True, allow_empty=False, write_only=True
    )

    class Meta:
        model = UserActivity
        fields = "__all__"

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

    def create(self, validated_data):
        guessed_movies = validated_data.pop("guessed_movies")
        user_activity = UserActivity.objects.create(**validated_data)
        for order, guessed_movie in enumerate(guessed_movies):
            Guess.objects.create(
                user_activity=user_activity, order=order, **guessed_movie
            )
        return user_activity
