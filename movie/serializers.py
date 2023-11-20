from rest_framework import serializers, exceptions
from .models import Movie, Contact, Feedback, FeedbackSubject


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
                self.Meta.exclude = ("name", "imdb_id")
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
