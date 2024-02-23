import operator
from django.db import models
from functools import reduce
from rest_framework.compat import distinct
from rest_framework.filters import SearchFilter


class PriorizedSearchFilter(SearchFilter):
    def filter_queryset(self, request, queryset, view):
        search_fields = self.get_search_fields(view, request)
        search_terms = self.get_search_terms(request)
        search_param = request.query_params.get(self.search_param, "")

        if not search_fields or not search_terms:
            return queryset

        orm_lookups = [
            self.construct_search(str(search_field)) for search_field in search_fields
        ]

        base = queryset
        querysets = []
        search_terms.insert(0, search_param)
        for search_term in search_terms:
            queries = [
                models.Q(**{orm_lookup: search_term}) for orm_lookup in orm_lookups
            ]
            when_conditions = [
                models.When(queries[i], then=models.Value(len(queries) - i - 1))
                for i in range(len(queries))
            ]
            querysets.append(
                queryset.filter(reduce(operator.or_, queries)).annotate(
                    priority=models.Case(
                        *when_conditions,
                        output_field=models.IntegerField(),
                        default=models.Value(-1)
                    )
                )
            )

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
