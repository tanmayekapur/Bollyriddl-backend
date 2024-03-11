from django import forms
from .models import Movie
from import_export.forms import ExportForm
from django.contrib.admin.widgets import FilteredSelectMultiple, AdminDateWidget


class AnalyticsForm(forms.Form):
    CHOICES = (
        ("guess_count", "No. of times any movie is guessed on given date"),
        ("min_max_movies_by_trial", "Most & Least guessed movie at given trial"),
        ("min_max_movies_by_date", "Most & Least guessed movie on given date"),
        (
            "time_taken",
            "Minimum, mean and median time taken in given guesses and date",
        ),
        ("guesses_count", "Minimum, mean and median guesses on given date"),
    )
    analytics_choice = forms.ChoiceField(label="Analytics Choice", choices=CHOICES)


class ArchiveForm(forms.Form):
    date = forms.DateField(label="Date", widget=AdminDateWidget())
    movies = forms.ModelMultipleChoiceField(
        label="Movies",
        queryset=Movie.objects.all().order_by("-id"),
        widget=FilteredSelectMultiple("Movies", is_stacked=False),
    )


class SelectiveExportForm(ExportForm):
    start_date = forms.DateField(
        label="Start Date",
        required=True,
        widget=forms.DateInput(attrs={"type": "date"}),
    )
    end_date = forms.DateField(
        label="End Date", required=True, widget=forms.DateInput(attrs={"type": "date"})
    )

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get("start_date")
        end_date = cleaned_data.get("end_date")

        if start_date > end_date:
            self.add_error("start_date", "Start Date cannot be greater than End Date")
        if end_date < start_date:
            self.add_error("end_date", "End Date cannot be less than Start Date")
        return cleaned_data
