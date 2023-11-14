from django.db import models

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
    genres = models.ManyToManyField(Genre, verbose_name="Genres")
    cast = models.ManyToManyField(Cast, verbose_name="Cast")
    writers = models.ManyToManyField(Writer, verbose_name="Writers")
    director = models.ForeignKey(
        Director, verbose_name="Director", on_delete=models.CASCADE
    )
    music_directors = models.ManyToManyField(
        MusicDirector, verbose_name="Music Directors"
    )
    production_house = models.ForeignKey(
        ProductionHouse, verbose_name="Production House", on_delete=models.CASCADE
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
