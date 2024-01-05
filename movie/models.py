from sortedm2m.fields import SortedManyToManyField
from django.db import models
import uuid

# Create your models here.


class Genre(models.Model):
    name = models.CharField("Name", unique=True, max_length=255)

    def __str__(self):
        return self.name

    def validate_unique(self, exclude):
        self.name = self.name.title()
        return super().validate_unique(exclude)

    def save(self, *args, **kwargs):
        self.name = self.name.title()
        super().save(*args, **kwargs)


class Cast(models.Model):
    name = models.CharField("Name", unique=True, max_length=255)

    def __str__(self):
        return self.name

    def validate_unique(self, exclude):
        self.name = self.name.title()
        return super().validate_unique(exclude)

    def save(self, *args, **kwargs):
        self.name = self.name.title()
        super().save(*args, **kwargs)


class Writer(models.Model):
    name = models.CharField("Name", unique=True, max_length=255)

    def __str__(self):
        return self.name

    def validate_unique(self, exclude):
        self.name = self.name.title()
        return super().validate_unique(exclude)

    def save(self, *args, **kwargs):
        self.name = self.name.title()
        super().save(*args, **kwargs)


class Director(models.Model):
    name = models.CharField("Name", unique=True, max_length=255)

    def __str__(self):
        return self.name

    def validate_unique(self, exclude):
        self.name = self.name.title()
        return super().validate_unique(exclude)

    def save(self, *args, **kwargs):
        self.name = self.name.title()
        super().save(*args, **kwargs)


class MusicDirector(models.Model):
    name = models.CharField("Name", unique=True, max_length=255)

    def __str__(self):
        return self.name

    def validate_unique(self, exclude):
        self.name = self.name.title()
        return super().validate_unique(exclude)

    def save(self, *args, **kwargs):
        self.name = self.name.title()
        super().save(*args, **kwargs)


class ProductionHouse(models.Model):
    name = models.CharField("Name", unique=True, max_length=255)

    def __str__(self):
        return self.name

    def validate_unique(self, exclude):
        self.name = self.name.title()
        return super().validate_unique(exclude)

    def save(self, *args, **kwargs):
        self.name = self.name.title()
        super().save(*args, **kwargs)


class Movie(models.Model):
    name = models.CharField("Name", unique=True, max_length=255)
    imdb_id = models.CharField("IMDB ID", unique=True, max_length=255)
    year = models.IntegerField("Year of Release", default=0)
    genres = SortedManyToManyField(Genre, verbose_name="Genres")
    cast = SortedManyToManyField(Cast, verbose_name="Cast")
    writers = SortedManyToManyField(Writer, verbose_name="Writers")
    directors = SortedManyToManyField(Director, verbose_name="Directors")
    music_directors = SortedManyToManyField(
        MusicDirector, verbose_name="Music Directors"
    )
    production_houses = SortedManyToManyField(
        ProductionHouse, verbose_name="Production Houses"
    )

    def __str__(self):
        return self.name

    def validate_unique(self, exclude):
        self.name = self.name.title()
        self.imdb_id = self.imdb_id.lower()
        return super().validate_unique(exclude)

    def save(self, *args, **kwargs):
        self.name = self.name.title()
        self.imdb_id = self.imdb_id.lower()
        super().save(*args, **kwargs)


class Archive(models.Model):
    date = models.DateField("Date", unique=True)
    movie = models.ForeignKey(Movie, verbose_name="Movie", on_delete=models.CASCADE)

    def __str__(self):
        return f"Archive - {self.movie}"


class Contact(models.Model):
    name = models.CharField("Name", max_length=255)
    email = models.EmailField("Email", max_length=255)
    subject = models.CharField("Subject", max_length=255)
    message = models.TextField("Message")

    def __str__(self):
        return self.name


class FeedbackSubject(models.Model):
    name = models.CharField("Name", unique=True, max_length=255)

    def __str__(self):
        return self.name

    def validate_unique(self, exclude):
        self.name = self.name.title()
        return super().validate_unique(exclude)

    def save(self, *args, **kwargs):
        self.name = self.name.title()
        super().save(*args, **kwargs)


class Feedback(models.Model):
    subjects = SortedManyToManyField(FeedbackSubject, verbose_name="Subjects")
    email = models.EmailField("Email", max_length=255)
    message = models.TextField("Message")

    def __str__(self):
        subjects = ", ".join([subject.name for subject in self.subjects.all()])
        return f"{self.email} - {subjects}"


class User(models.Model):
    uuid = models.UUIDField("User ID", default=uuid.uuid4, unique=True, editable=False)

    def __str__(self):
        return str(self.uuid)


class Guess(models.Model):
    _sort_field_name = "order"

    user_activity = models.ForeignKey("UserActivity", on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    time_taken = models.DurationField("Time Taken")
    order = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.movie} - {self.time_taken}"

    class Meta:
        verbose_name_plural = "guesses"


class UserActivity(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    guessed_movies = SortedManyToManyField(
        Movie,
        through=Guess,
        verbose_name="Guessed Movies",
        sort_value_field_name="order",
    )
    start_time = models.DateTimeField("Start Time")
    end_time = models.DateTimeField("End Time")

    @property
    def guessed_movies_count(self):
        return self.guessed_movies.count()

    @property
    def total_time(self):
        return self.end_time - self.start_time

    @property
    def winner(self):
        if Archive.objects.filter(date=self.start_time.date()).exists():
            mystery_movie = Archive.objects.get(date=self.start_time.date()).movie
            if self.guess_set.last().movie.id == mystery_movie.id:
                return True
        return False

    class Meta:
        verbose_name_plural = "user activities"
