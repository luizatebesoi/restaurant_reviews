from django.shortcuts import render, get_object_or_404
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from .models import Restaurant, Review
from .filters import RestaurantFilter, ReviewFilter, HomeFilter
from django.views.generic.list import ListView
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


def detail(request, rest_id):
    restaurant = get_object_or_404(Restaurant, pk=rest_id)
    reviews = Review.objects.filter(rest_key_id=rest_id).order_by("-review_date")
    myFilter = ReviewFilter(request.GET, queryset=reviews)
    reviews = myFilter.qs
    length = len(reviews)
    return render(request, 'detail.html', {"restaurant": restaurant, "reviews": reviews,
                                           "myFilter": myFilter,
                                           "length": length
                                           })


def home(request):
    restaurants = Restaurant.objects.order_by('-reviews_number')
    myFilter = HomeFilter(request.GET, queryset=restaurants)
    restaurants = myFilter.qs
    return render(request, 'home.html', {"myFilter": myFilter,
                                         "restaurants": restaurants})


def restaurants(request):
    restaurants = Restaurant.objects.order_by('-reviews_number')
    city = ''
    if 'city' in request.GET:
        city = request.GET['city']
        if city != "":
            restaurants = restaurants.filter(city__iexact=city)
        else:
            city = "toata tara"
    else:
        city = "toata tara"
    myFilter = RestaurantFilter(request.GET, queryset=restaurants)
    restaurants = myFilter.qs
    length = len(restaurants)
    return render(request, "restaurants.html", {"restaurants": restaurants[:100],
                                                "myFilter": myFilter,
                                                "length": length,
                                                "city": city})
