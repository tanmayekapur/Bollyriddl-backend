from import_export.resources import ModelResource
from .models import Movie


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

            getattr(obj, field_name).set(related_objects)

        else:
            # Use the default behavior for other fields
            super().import_field(field, obj, data)


class MovieResource(RelatedResourceMixin):
    """
    Resource class for Movie model.
    """

    class Meta:
        model = Movie

    def before_import_row(self, row, **kwargs):
        """
        Override before_import_row to handle unique constraint violations.
        """
        name = row.get("name", None)
        imdb_id = row.get("imdb_id", None)
        if name:
            if Movie.objects.filter(name=name).exists():
                row["id"] = Movie.objects.get(name=name).id

        if imdb_id:
            if Movie.objects.filter(imdb_id=imdb_id).exists():
                row["id"] = Movie.objects.get(imdb_id=imdb_id).id

        super().before_import_row(row, **kwargs)
