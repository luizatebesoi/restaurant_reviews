import django_filters
from django.forms.widgets import TextInput
from .models import *


class RestaurantFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(label="Restaurant", field_name="search_name", lookup_expr="icontains",
                                     widget=TextInput(attrs={'placeholder': 'restaurant..'}))
    categories = django_filters.CharFilter(label="Categorie", field_name="categories", lookup_expr="icontains",
                                           widget=TextInput(attrs={'placeholder': 'pizza, burger, paste..'}))
    city = django_filters.ChoiceFilter(label="Oras", choices=cities_choices, empty_label="Toate orasele")

    class Meta:
        model = Restaurant
        fields = {"city": ["exact"]}


class ReviewFilter(django_filters.FilterSet):
    review = django_filters.CharFilter(label="Cauta in review-uri:", lookup_expr="icontains", field_name="review",
                                       widget=TextInput(attrs={'placeholder': 'pizza, burger, paste..'}))
    source = django_filters.ChoiceFilter(label="Sursa review", choices=review_sources, empty_label="Toate platformele")

    class Meta:
        model = Review
        fields = {"source": ["exact"]}


class HomeFilter(django_filters.FilterSet):
    city = django_filters.ChoiceFilter(label="Oras", choices=cities_choices, empty_label="Toate orasele")

    class Meta:
        model = Restaurant
        fields = {"city": ["exact"]}
