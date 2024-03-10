import random
from django import forms
from collections import Counter
from statistics import mean, median
from django.contrib import messages
from django.urls import path, reverse
from datetime import datetime, timedelta
from django.http import HttpResponseRedirect
from import_export.resources import ModelResource
from django.template.response import TemplateResponse
from .models import Movie, Archive, UserActivity, Guess
from django.contrib.admin.widgets import FilteredSelectMultiple, AdminDateWidget


class RelatedResourceMixin(ModelResource):
    """
    A mixin to handle importing related fields with many-to-many relationships.
    """

    def import_field(self, field, obj, data, is_m2m=False, **kwargs):
        """
        Override the import_field method to handle many-to-many relationships.
        """

        if is_m2m:
            # Handle many-to-many relationships
            field_name = field.column_name
            values = data.get(field_name, None)
            related_model = getattr(obj, field_name).model
            related_objects = []

            if values:
                for name in values:
                    related_object = related_model.objects.get_or_create(name=name)[0]
                    related_objects.append(related_object)

            for rel_obj in related_objects:
                getattr(obj, field_name).add(rel_obj)

        else:
            # Use the default behavior for other fields
            super().import_field(field, obj, data)


class AnalyticsForm(forms.Form):
    movie = forms.ModelChoiceField(
        label="Movie",
        queryset=Movie.objects.all().order_by("-id"),
        widget=forms.Select(attrs={"autocomplete": "off"}),
    )
    guesses = forms.IntegerField(label="Number of Guesses", min_value=0)
    trial = forms.IntegerField(label="Trial", min_value=0)
    date = forms.DateField(label="Date", widget=AdminDateWidget())


class AnalyticsMixin:
    analytics_change_list_template = "admin/analytics/change_list_analytics.html"
    analytics_template_name = "admin/analytics/analytics.html"
    analytics_form_class = AnalyticsForm

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.change_list_template = self.analytics_change_list_template

    def get_model_info(self):
        app_label = self.model._meta.app_label
        return (app_label, self.model._meta.model_name)

    def get_urls(self):
        urls = super().get_urls()
        info = self.get_model_info()
        my_urls = [
            path(
                "analytics/",
                self.admin_site.admin_view(self.analytics),
                name="%s_%s_analytics" % info,
            ),
        ]
        return my_urls + urls

    def analytics(self, request, *args, **kwargs):
        context = {
            "today_analytics": self.get_today_analytics(),
        }

        try:
            if set(context["today_analytics"].values()) == {(None, None), None, 7}:
                context["today_analytics"] = None
        except:
            pass

        if request.method == "POST":
            analytics_form = AnalyticsForm(request.POST)
            if analytics_form.is_valid():
                analytics_data = self.get_analytics_data(analytics_form.cleaned_data)
                context.update(
                    {
                        "form": analytics_form,
                        "analytics_data": analytics_data,
                    }
                )
        else:
            analytics_form = AnalyticsForm()

        context.update(self.admin_site.each_context(request))
        context.update(
            {
                "title": "Analytics",
                "opts": self.model._meta,
                "form": analytics_form,
                "media": analytics_form.media,
            }
        )

        request.current_app = self.admin_site.name
        return TemplateResponse(request, [self.analytics_template_name], context)

    def guess_count(self, form_data):
        movie = form_data["movie"]
        date = form_data["date"]

        if not movie:
            return None

        guess_count = UserActivity.objects.filter(
            guessed_movies__id=movie.id, start_time__date=date
        ).count()
        return guess_count

    def min_max_movies(self, form_data, target, by):
        trial = form_data["trial"] - 1
        date = form_data["date"]

        if by == "trial":
            guesses = Guess.objects.filter(order=trial)

        if by == "date":
            guesses = Guess.objects.filter(user_activity__start_time__date=date)

        if not guesses.exists():
            return None

        movie_idx = list(guesses.values_list("movie__id", flat=True))
        occurences = Counter(movie_idx)

        occurence = target(occurences.values())
        movies = []

        for key in occurences.keys():
            if occurences[key] == occurence:
                movies.append(key)

        movies = list(map(lambda x: Movie.objects.get(id=x).name, movies))
        return movies

    def time_taken(self, form_data):
        date = form_data["date"]
        guesses = form_data["guesses"]

        user_activities = UserActivity.objects.filter(start_time__date=date)
        filtered_user_activities = [
            user_activity
            for user_activity in user_activities
            if user_activity.guessed_movies_count == guesses and user_activity.winner
        ]

        if len(filtered_user_activities) == 0:
            return None

        min_time_taken = min(
            filtered_user_activities, key=lambda ua: ua.total_time
        ).total_time

        time_taken_values = [
            user_activity.total_time.seconds for user_activity in user_activities
        ]
        mean_time_taken = timedelta(seconds=mean(time_taken_values))
        median_time_taken = timedelta(seconds=median(time_taken_values))

        min_time_taken = f"{min_time_taken.seconds // 3600} hours {(min_time_taken.seconds // 60) % 60} minutes and {min_time_taken.seconds % 60} seconds"
        mean_time_taken = f"{mean_time_taken.seconds // 3600} hours {(mean_time_taken.seconds // 60) % 60} minutes and {mean_time_taken.seconds % 60} seconds"
        median_time_taken = f"{median_time_taken.seconds // 3600} hours {(median_time_taken.seconds // 60) % 60} minutes and {median_time_taken.seconds % 60} seconds"

        return min_time_taken, mean_time_taken, median_time_taken

    def guesses_count(self, form_data):
        date = form_data["date"]

        user_activities = UserActivity.objects.filter(start_time__date=date)
        filtered_user_activities = [
            user_activity for user_activity in user_activities if user_activity.winner
        ]
        if len(filtered_user_activities) == 0:
            return None

        guesses_values = [
            user_activity.guessed_movies_count
            for user_activity in filtered_user_activities
        ]
        min_guesses = min(guesses_values)
        mean_guesses = mean(guesses_values)
        median_guesses = median(guesses_values)
        return min_guesses, mean_guesses, median_guesses

    def get_today_analytics(self):
        date = datetime.today().date()
        movie = None
        if Archive.objects.filter(date=date).exists():
            movie = Archive.objects.get(date=date).movie

        form_data = {
            "movie": movie,
            "guesses": 7,
            "trial": 7,
            "date": date,
        }

        return {
            "movie": movie.name if movie else None,
            "guesses": form_data["guesses"],
            "trial": form_data["trial"],
            "guess_count": self.guess_count(form_data),
            "min_max_movies_by_trial": (
                self.min_max_movies(form_data, min, "trial"),
                self.min_max_movies(form_data, max, "trial"),
            ),
            "min_max_movies_by_date": (
                self.min_max_movies(form_data, min, "date"),
                self.min_max_movies(form_data, max, "date"),
            ),
            "time_taken": self.time_taken(form_data),
            "guesses_count": self.guesses_count(form_data),
        }

    def get_analytics_data(self, form_data):
        return {
            "movie": form_data["movie"].name,
            "guesses": form_data["guesses"],
            "trial": form_data["trial"],
            "date": form_data["date"].strftime("%Y-%m-%d"),
            "guess_count": self.guess_count(form_data),
            "min_max_movies_by_trial": (
                self.min_max_movies(form_data, min, "trial"),
                self.min_max_movies(form_data, max, "trial"),
            ),
            "min_max_movies_by_date": (
                self.min_max_movies(form_data, min, "date"),
                self.min_max_movies(form_data, max, "date"),
            ),
            "time_taken": self.time_taken(form_data),
            "guesses_count": self.guesses_count(form_data),
        }


class ArchiveForm(forms.Form):
    date = forms.DateField(label="Date", widget=AdminDateWidget())
    movies = forms.ModelMultipleChoiceField(
        label="Movies",
        queryset=Movie.objects.all().order_by("-id"),
        widget=FilteredSelectMultiple("Movies", is_stacked=False),
    )


class ArchiveMixin:
    archive_change_list_template = "admin/archive/change_list_archive.html"
    archive_template_name = "admin/archive/archive.html"
    archive_form_class = ArchiveForm

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.change_list_template = self.archive_change_list_template

    def get_model_info(self):
        app_label = self.model._meta.app_label
        return (app_label, self.model._meta.model_name)

    def get_urls(self):
        urls = super().get_urls()
        info = self.get_model_info()
        my_urls = [
            path(
                "bulk-add/",
                self.admin_site.admin_view(self.bulk_add),
                name="%s_%s_bulk_add" % info,
            ),
        ]
        return my_urls + urls

    def bulk_add(self, request, *args, **kwargs):
        context = {}

        if request.method == "POST":
            archive_form = ArchiveForm(request.POST)
            if archive_form.is_valid():
                date = archive_form.cleaned_data["date"]
                movies = list(archive_form.cleaned_data["movies"])
                movies_count = len(movies)

                dates = []
                start_date = date
                count = movies_count
                while count > 0:
                    if not Archive.objects.filter(date=start_date).exists():
                        dates.append(start_date)
                        count -= 1
                    start_date += timedelta(days=1)

                random.shuffle(movies)

                instances = [
                    Archive(date=dates[idx], movie=movie)
                    for idx, movie in enumerate(movies)
                ]

                Archive.objects.bulk_create(instances)

                messages.success(
                    request, f"{movies_count} archives was added successfully."
                )
                return HttpResponseRedirect(reverse("admin:movie_archive_changelist"))
        else:
            archive_form = ArchiveForm()

        context.update(self.admin_site.each_context(request))
        context.update(
            {
                "title": "Bulk Add archive",
                "opts": self.model._meta,
                "form": archive_form,
                "media": archive_form.media,
            }
        )
        request.current_app = self.admin_site.name

        return TemplateResponse(request, [self.archive_template_name], context)
