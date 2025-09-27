import django_filters
from .models import Borrowing


class BorrowingFilter(django_filters.FilterSet):
    is_active = django_filters.BooleanFilter(method="filter_is_active")
    user_id = django_filters.NumberFilter(field_name="user__id")

    class Meta:
        model = Borrowing
        fields = ["is_active","user_id"]

    def filter_is_active(self, queryset, name, value):
        if value is True:
            return queryset.filter(actual_return_date__isnull=True)
        if value is False:
            return queryset.filter(actual_return_date__isnull=False)
        return queryset
