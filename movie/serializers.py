from rest_framework import serializers
from .models import Movie, Contact


class MovieSerializer(serializers.ModelSerializer):
    director = serializers.StringRelatedField()
    production_house = serializers.StringRelatedField()
    genres = serializers.StringRelatedField(many=True)
    cast = serializers.StringRelatedField(many=True)
    writers = serializers.StringRelatedField(many=True)
    music_directors = serializers.StringRelatedField(many=True)

    class Meta:
        model = Movie
        exclude = ("id", "imdb_id")


class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = "__all__"
