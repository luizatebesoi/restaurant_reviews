import os
from os.path import dirname
import requests
from bs4 import BeautifulSoup
from csv import DictWriter


def get_reviews_info(link, cities, category):
    reviews_info = []
    for city in cities:
        response = requests.get(link + city + "/categorie/" + category)
        response.encoding = "utf-8"
        soup = BeautifulSoup(response.text, "html.parser")
        restaurants = soup.find_all(class_="restaurant js-add-coords")
        for restaurant in restaurants:
            name = restaurant.find(class_="resto_name").find("h2").get_text().strip()
            reviews_no = restaurant.find(class_="rating_box").find("span").find("span").get_text().strip()
            restaurant_categories = restaurant.find(class_="resto_specific").find("span").get_text().strip()
            if restaurant.find(class_="order_min").find(class_="price"):
                minimum_order = restaurant.find(class_="order_min").find(class_="price").get_text().strip()
            else:
                minimum_order = restaurant.find(class_="order_min").find("b").get_text().strip()
            delivery_fee = restaurant.find(class_="delivery_price").get_text().strip()
            restaurant_rating = restaurant.find(class_="rating_box").find("b").get_text().strip()
            restaurant_page_href = restaurant["href"]
            rest_image = restaurant.find(class_="resto_pic").find("img")["src"]

            restaurant_page_response = requests.get(restaurant_page_href + "/#reviews")
            restaurant_page_response.encoding = "utf-8"
            soup = BeautifulSoup(restaurant_page_response.text, "html.parser")
            if soup.find(class_="restaurant_info"):
                address = soup.find(class_="restaurant_info").find("span").get_text().strip()
            else:
                address = None
            all_reviews = soup.find_all(class_="review_box")
            if len(all_reviews) > 0:
                for review in all_reviews:
                    review_descr = review.find("p").get_text().strip()
                    review_author = review.find(class_="review_author").get_text().split(" - ")[0].strip()
                    review_rating = review.find(class_="review_stars").find("span").get_text().strip()
                    review_date = review.find(class_="review_author").get_text().split(" ")[-1].strip()
                    reviews_info.append({"name": name,
                                         "review": review_descr,
                                         "review_date": review_date,
                                         "review_rating": review_rating,
                                         "restaurant_rating": restaurant_rating,
                                         "reviews_no": reviews_no,
                                         "city": city,
                                         "address": address,
                                         "author": review_author,
                                         "categories": restaurant_categories,
                                         "source": "tazz",
                                         "tazz_minimum_order": minimum_order,
                                         "tazz_delivery_fee": delivery_fee,
                                         "tazz_restaurant_page_href": restaurant_page_href,
                                         "rest_image": rest_image
                                         })
                    print(name, address, review_author, restaurant_categories, minimum_order, delivery_fee, rest_image,
                          city)
            else:
                reviews_info.append({"name": name,
                                     "review": None,
                                     "review_date": None,
                                     "review_rating": None,
                                     "restaurant_rating": restaurant_rating,
                                     "reviews_no": reviews_no,
                                     "city": city,
                                     "address": address,
                                     "author": None,
                                     "categories": restaurant_categories,
                                     "source": "foodpanda",
                                     "tazz_minimum_order": minimum_order,
                                     "tazz_delivery_fee": delivery_fee,
                                     "tazz_restaurant_page_href": restaurant_page_href,
                                     "rest_image": rest_image
                                     })
                print(name, address, restaurant_categories, minimum_order, delivery_fee, rest_image, city)
    return reviews_info


def write_restaurants_info_to_csv(reviews_info):
    with open(os.path.join(dirname(dirname(__file__)), "media/csv/tazz.csv"), "w", encoding="utf-8",
              newline="") as file:
        headers = ["name",
                   "review",
                   "review_date",
                   "review_rating",
                   "restaurant_rating",
                   "reviews_no",
                   "city",
                   "address",
                   "author",
                   "categories",
                   "source",
                   "tazz_minimum_order",
                   "tazz_delivery_fee",
                   "tazz_restaurant_page_href",
                   "rest_image"]
        csv_writer = DictWriter(file, fieldnames=headers)
        csv_writer.writeheader()
        for review in reviews_info:
            csv_writer.writerow(review)


url = "https://tazz.ro/"
cities = ("bucuresti", "cluj-napoca", "timisoara", "iasi", "brasov",
          "oradea", "constanta", "arad", "sibiu", "galati", "pitesti",
          "craiova", "ploiesti", "baia-mare", "braila", "suceava",
          "deva", "alba-iulia", "resita", "botosani", "roman", "targu-mures")
category = "restaurant"

cities1 = ("deva", "roman", "cluj-napoca")
