import operator
from django.db import models
from functools import reduce
from rest_framework.compat import distinct
from rest_framework.filters import SearchFilter


# Custom search filter with prioritization
class PriorizedSearchFilter(SearchFilter):
    def filter_queryset(self, request, queryset, view):
        """
        Filter the queryset based on the provided search terms and search fields.

        Args:
            request (HttpRequest): The HTTP request object.
            queryset (QuerySet): The initial queryset to be filtered.
            view (View): The view object that is using this filter.

        Returns:
            QuerySet: The filtered queryset.

        This function takes the search terms and search fields provided in the request
        and constructs a queryset that matches the search criteria. The search terms are
        matched against the search fields using the OR operator. The resulting queryset
        is annotated with a priority field based on the order of the search terms. The
        queryset is then ordered by the priority field in descending order.

        If the search term starts with a caret (^), it is treated as a prefix search.
        The prefix search queryset is separated from the main queryset and combined
        with it using the OR operator.

        If the queryset contains many-to-many relationships, duplicate items may be
        present in the resulting queryset. To avoid this, the queryset is filtered using
        the distinct() function, which removes duplicates based on the base queryset.
        """

        search_fields = self.get_search_fields(view, request)
        search_terms = self.get_search_terms(request)
        search_param = request.query_params.get(self.search_param, "")

        if not search_fields or not search_terms:
            return queryset

        # Construct ORM lookups for each search field
        orm_lookups = [
            self.construct_search(str(search_field)) for search_field in search_fields
        ]

        # Initial queryset
        base = queryset
        querysets = []
        search_terms.insert(0, search_param)
        for search_term in search_terms:
            # Construct queries for each ORM lookup
            queries = [
                models.Q(**{orm_lookup: search_term}) for orm_lookup in orm_lookups
            ]
            # Construct 'WHEN' conditions for prioritization
            when_conditions = [
                models.When(queries[i], then=models.Value(len(queries) - i - 1))
                for i in range(len(queries))
            ]
            # Filter queryset and annotate with priority
            querysets.append(
                queryset.filter(reduce(operator.or_, queries)).annotate(
                    priority=models.Case(
                        *when_conditions,
                        output_field=models.IntegerField(),
                        default=models.Value(-1)
                    )
                )
            )

        # Separate startswith queryset and main queryset
        startswith_queryset = querysets.pop(0)
        queryset = reduce(operator.and_, querysets).order_by("-priority")
        querysets = [startswith_queryset, queryset]
        queryset = reduce(operator.or_, querysets).order_by("-priority")

        if self.must_call_distinct(queryset, search_fields):
            # Filtering against a many-to-many field requires us to
            # call queryset.distinct() in order to avoid duplicate items
            # in the resulting queryset.
            # We try to avoid this if possible, for performance reasons.
            queryset = distinct(queryset, base)
        return queryset
