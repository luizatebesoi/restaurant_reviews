import os
from os.path import dirname
import requests
from bs4 import BeautifulSoup
from csv import DictWriter


def get_reviews_info(link, search_link, cities):
    reviews_info = []
    for city in cities:
        response = requests.get(search_link+city[1])
        response.encoding = "utf-8"
        soup_cities = BeautifulSoup(response.text, "lxml")
        restaurants_list_boxes = soup_cities.find_all(class_ = "vendor-list")
        restaurants = []
        for list in restaurants_list_boxes:
            restaurants1 = list.find_all("a")
            restaurants.extend(restaurants1)
        for restaurant in restaurants:
            name = restaurant.find(class_="name fn").get_text().strip()
            delivery_info = restaurant.find(class_="mov-df-extra-info").find_all("li")
            minimum_order = delivery_info[0].find("strong").get_text()
            delivery_fee = delivery_info[1].find("strong").get_text()
            restaurant_categories = []
            categories = restaurant.find(class_ = "vendor-characteristic").find_all("span")
            for item in categories:
                restaurant_categories.append(item.get_text().strip())
            categories_str = ', '.join(restaurant_categories)

            restaurant_page_href = restaurant["href"]
            restaurant_info = requests.get(link + restaurant_page_href + "#restaurant-info")
            restaurant_info.encoding = "utf-8"
            rest_info_soup = BeautifulSoup(restaurant_info.text, "html.parser")
            if rest_info_soup.find(class_ = "vendor-location") != None:
                address = rest_info_soup.find(class_ = "vendor-location").get_text().strip()
            else:
                address = ""
            restaurant_page_response = requests.get(link + restaurant_page_href)
            restaurant_page_response.encoding = "utf-8"
            soup = BeautifulSoup(restaurant_page_response.text, "html.parser")
            if soup.find(class_="ratings-component"):
                reviews_no = soup.find(class_="ratings-component").find(class_="count").get_text().strip()
            else:
                reviews_no = None
            if soup.find(class_="ratings-component"):
                restaurant_rating = soup.find(class_="ratings-component").find(class_="rating").find("strong").get_text().strip()
            else:
                restaurant_rating = None
            if soup.find(class_="vendor-header"):
                if soup.find(class_="vendor-header").find("div")["data-src"]:
                    rest_image = soup.find(class_="vendor-header").find("div")["data-src"]
                else:
                    rest_image = None
            else:
                rest_image = None
            all_reviews = soup.find_all(class_ = "review-component hreview")
            if len(all_reviews) > 0:
                for review in all_reviews:
                    review_descr = review.find(class_ = "description").get_text().strip()
                    review_author = review.find(class_ = "reviewer vcard").find(class_ = "fn").get_text().strip()
                    if review.find("strong"):
                        review_rating = review.find("strong").get_text().strip()
                    else:
                        review_rating = None
                    review_date = review.find(class_ = "review-date dtreviewed").get_text().strip()
                    reviews_info.append({"name" : name,
                                         "review" : review_descr,
                                         "review_date" : review_date,
                                         "review_rating" : review_rating,
                                         "restaurant_rating" : restaurant_rating,
                                         "reviews_no" : reviews_no,
                                         "city" : city[0],
                                         "address" : address,
                                         "author" : review_author,
                                         "categories" : categories_str,
                                         "source": "foodpanda",
                                         "fp_minimum_order": minimum_order,
                                         "fp_delivery_fee": delivery_fee,
                                         "fp_restaurant_page_href": restaurant_page_href,
                                         "rest_image": rest_image

                                         })

                    print(name, address, review_author, categories_str, minimum_order, delivery_fee, rest_image, city[0], reviews_no, restaurant_rating)
            else:
                reviews_info.append({"name" : name,
                                     "review" : None,
                                     "review_date" : None,
                                     "review_rating" : None,
                                     "restaurant_rating" : restaurant_rating,
                                     "reviews_no" : reviews_no,
                                     "city" : city[0],
                                     "address" : address,
                                     "author" : None,
                                     "categories" : categories_str,
                                     "source": "foodpanda",
                                     "fp_minimum_order": minimum_order,
                                     "fp_delivery_fee": delivery_fee,
                                     "fp_restaurant_page_href": restaurant_page_href,
                                     "rest_image": rest_image

                                         })

                print(name, address, categories_str, minimum_order, delivery_fee, rest_image, city[0], reviews_no, restaurant_rating)
    return reviews_info


def write_restaurants_info_to_csv(reviews_info):
    with open(os.path.join(dirname(dirname(__file__)), "media/csv/foodpanda.csv"), "w", encoding = "utf-8", newline = "") as file:
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
                   "fp_minimum_order",
                   "fp_delivery_fee",
                   "fp_restaurant_page_href",
                   "rest_image"]
        csv_writer = DictWriter(file, fieldnames= headers)
        csv_writer.writeheader()
        for review in reviews_info:
            csv_writer.writerow(review)


base_search_url = "https://www.foodpanda.ro/restaurants/"
base_url = "https://www.foodpanda.ro"


cities = (("bucuresti", "new?lat=44.42733610000001&lng=26.1039363&vertical=restaurants"),
          ("cluj-napoca", "new?lat=46.77028199999999&lng=23.588339&vertical=restaurants"),
          ("timisoara", "new?lat=45.7540172&lng=21.225833&vertical=restaurants"),
          ("iasi", "new?lat=47.164872&lng=27.586652&vertical=restaurants"),
          ("brasov", "new?lat=45.6579062&lng=25.6010367&vertical=restaurants"),
          ("oradea", "new?lat=47.05545069999999&lng=21.9281201&vertical=restaurants"),
          ("constanta", "new?lat=44.1790003&lng=28.6508752&vertical=restaurants"),
          ("arad", "new?lat=46.1742854&lng=21.31367939999999&vertical=restaurants"),
          ("sibiu", "new?lat=45.7968723&lng=24.1500499&vertical=restaurants"),
          ("galati", "new?lat=45.43949840000001&lng=28.0367127&vertical=restaurants"),
          ("pitesti", "restaurants/new?lat=44.8582518&lng=24.8746943&vertical=restaurants"),
          ("craiova", "restaurants/new?lat=44.3193555&lng=23.7942362&vertical=restaurants"),
          ("ploiesti", "new?lat=44.9435593&lng=26.0204985&vertical=restaurants"),
          ("baia-mare", "new?lat=47.659321&lng=23.5818455&vertical=restaurants"),
          ("buzau", "new?lat=45.1370346&lng=26.8160698&vertical=restaurants"),
          ("braila", "new?lat=45.2730617&lng=27.9736206&vertical=restaurants"),
          ("bacau", "new?lat=46.5667907&lng=26.9147742&vertical=restaurants"),
          ("targu-mures", "new?lat=46.5384969&lng=24.5513527&vertical=restaurants"),
          ("mioveni", "new?lat=44.95731199999999&lng=24.947192&vertical=restaurants"),
          ("ramnicu-valcea", "new?lat=45.1007755&lng=24.3698772&vertical=restaurants"),
          ("targu-jiu", "new?lat=45.031455&lng=23.2694971&vertical=restaurants"),
          ("drobeta-turnu severin", "new?lat=44.6367984&lng=22.6601473&vertical=restaurants"),
          ("targoviste", "new?lat=44.9122468&lng=25.4537877&vertical=restaurants"),
          ("alba-iulia", "new?lat=46.0733123&lng=23.5806754&vertical=restaurants"),
          ("deva", "new?lat=45.86625739999999&lng=22.9143737&vertical=restaurants"),
          ("botosani", "new?lat=47.74076729999999&lng=26.6663562&vertical=restaurants"),
          ("suceava", "new?lat=47.6644441&lng=26.2691954&vertical=restaurants"),
          ("bistrita", "new?lat=47.139792&lng=24.488501&vertical=restaurants"),
          ("satu-mare", "new?lat=47.8018509&lng=22.857749&vertical=restaurants"),
          ("piatra-neamt", "new?lat=46.93531100000001&lng=26.3789909&vertical=restaurants"),
          ("focsani", "new?lat=45.6964529&lng=27.184108&vertical=restaurants"),
          ("sebes", "new?lat=45.9594602&lng=23.5664861&vertical=restaurants")
          )
