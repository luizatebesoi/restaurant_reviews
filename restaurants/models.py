from django.db import models
from .choices import cities_choices, review_sources


# Create your models here.
class Restaurant(models.Model):
    name = models.CharField(max_length=800)
    city = models.CharField(max_length=800, choices=cities_choices)
    address = models.CharField(max_length=800)
    categories = models.CharField(max_length=800, null=True)
    tazz_page_href = models.URLField(max_length=800, null=True)
    fp_page_href = models.URLField(max_length=800, null=True)
    image = models.URLField(max_length=1000, null=True)
    unique_id = models.CharField(max_length=1000, null=True)
    internal_address = models.CharField(max_length=800)
    street_no = models.CharField(max_length=500, null=True)
    internal_name = models.CharField(max_length=800)
    tazz_delivery_fee = models.CharField(max_length=800, null=True)
    fp_delivery_fee = models.CharField(max_length=800, null=True)
    tazz_minimum_order = models.CharField(max_length=800, null=True)
    fp_minimum_order = models.CharField(max_length=800, null=True)
    restaurant_rating = models.FloatField(null=True)
    reviews_number = models.IntegerField(null=True)
    reviews_total = models.FloatField(blank=True)
    img = models.ImageField(upload_to='restaurants/images', null=True, max_length=1000)


#ImageField(upload_to='restaurants/images', null=True, max_length=1000)
    def __str__(self):
        return self.name


class Review(models.Model):
    review = models.CharField(max_length=4000)
    review_date = models.DateField(auto_now_add=True)
    review_rating = models.FloatField(null=True)
    author = models.CharField(max_length=4000, null=True)
    source = models.CharField(max_length=4000, choices=review_sources)
    rest_key = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    unique_id = models.CharField(max_length=1000, null=True)
