import pandas as pd
import psycopg2 as psg
from csv import DictWriter
import images_download as img
import getting_reviews_from_foodpanda as fp
import getting_reviews_from_tazz as tazz
from os.path import dirname
import os


# Setting the primary key column
def set_keys(start_value, data_length):
    """
    It takes in a start value and the length of the data rows
    and it returns a list of unique autoincremented keys.
    Parameters:
        1. start_value = int value from where the keys values
                        start.
        2. data_length = the number of rows in the data.
    """
    keys = []
    for i in range(start_value, start_value + data_length):
        keys.append(i)
    return keys


# Group together the restaurants
def group_rest(info):
    accumulator = []
    results = []
    for item in info:
        if item[0] not in accumulator:
            results.append(item[1])
            accumulator.append(item[0])
    return results


def image_titles(links):
    results = []
    for link in links:
        if pd.notna(link):
            filename = link.split("/")[-1]
            file = os.path.join(os.path.join(dirname(dirname(__file__)), "media/restaurants/images/"), filename)
            results.append(file)
        else:
            results.append(None)
    return results


def capitalize_city(x):
    if "-" in x:
        splitted_x = x.split("-")
        first_word = splitted_x[0]
        second_word = splitted_x[1]
        if " " in second_word:
            third_word = second_word.split(" ")[1]
            second_word = second_word.split(" ")[0]
            return '-'.join((first_word.capitalize(), second_word.capitalize())) + " " + third_word.capitalize()
        else:
            return '-'.join((first_word.capitalize(), second_word.capitalize()))

    else:
        return x.capitalize()


# Group the restaurants unique_ids:
def group_unique_ids(initial, comparison):
    results = []
    for item in initial:
        item_key = item[0]
        item_unique_id = item[1]

        for i in comparison:
            i_key = i[0]
            i_unique_id = i[1]
            if item_key == i_key:
                item_unique_id += ", " + i_unique_id

        results.append(item_unique_id)
    return results


# Replacing the month string with int
def replace_dayormonthstr(x, li):
    """
    It replaces the x month string with the corresponding int
    value from the li tuple / list.
    Parameters:
        1. x = month string that needs to be replaced
        2. li = tuple or list containing tuples of month strings
                and their corresponding int value
    """
    for item in li:
        if x == item[0]:
            x = item[1]
    return x


# Standardizing city names
def value_change(x, old_value, new_value):
    """
    It checks if a city value is equal to an old value which
    needs to be replaced. If it is equal, then it replaces it
    with the new value.
    Parameters:
        1. x = the initial city string.
        2. old_value = the string value that needs to be replaced.
        3. new_value = the string value that the old value will be
                        replaced with.
    """
    if x == old_value:
        return new_value
    else:
        return x


# Computing the sum of reviews based on rating and total number
# of reviews
def sum_of_reviews(x, y):
    """
    It computes the total sum of reviews of a restaurant
    based on the restaurant number of reviews and restaurant
    rating.
    Parameters:
        1. x = restaurant rating as a float number.
        2. y = reviews number as an int.
    """
    if pd.isnull(x):
        return 0
    else:
        return x * y


# Taking care of zero and null values
def convert_zero_to_nan(x):
    if x == 0:
        return None
    else:
        return x


def string_to_float(x):
    if x == "Fara":
        return None
    else:
        return float(x)


def value_to_int(x):
    if pd.isnull(x):
        return 0
    else:
        return int(x)


def change_address_nan(x):
    if pd.isnull(x):
        return ''
    else:
        return x


def change_street_number_nan(x):
    if pd.isnull(x):
        return ''
    else:
        return int(x)


# Delivery fee processing function
def change_delivery_fee(x):
    x = x.strip()
    if len(x.split()) == 1:
        if "Livrare" in x:
            x = x.replace("Livrare", "Livrare gratuită")
    if x != "Livrare gratuită":
        x = x.replace(",", ".")
        if "RON" in x:
            x = x.replace("RON", "Lei")
        if x.split()[0] != "Livrare":
            x = "Livrare " + x
        if len(x.split()) > 1:
            if "." in x.split()[1]:
                x = x
            else:
                splitted_x = x.split()
                x = splitted_x[0] + " " + splitted_x[1] + ".00 " + splitted_x[2]
    return x


# Minimum order processing function
def change_minimum_order(x):
    x = x.strip()
    if "Fara" in x:
        x = x.replace("Fara", "Fără comanda minima")
    elif "Fără" in x:
        x = x.replace("Fără", "Fără comanda minima")
    if "," in x:
        x = x.replace(",", ".")
    if '.' not in x and len(x.split()) < 3:
        x = x.split()[0] + ".00 Lei"
    if "RON" in x:
        x = x.replace("RON", "Lei")
    return x


# Restaurant names cleaning
def name_cleaning(x, special_chars, special_letters, common_words, cities):
    """
    It cleans the restaurant names by removing: special
    characters, common words, cities names and by replacing
    special letters with normal ones.
    Parameters:
        1. x = the restaurant name string that needs to be cleaned.
        2. special_chars = a list or tuple of special
                            characters that need to be removed.
        3. special_letters = a list or tuple of special letters
                                that need to be replaced with
                                normal letters.
        4. common_words = a list or tuple of common address words
                            that need to be removed from the address.
        5. cities = a list or tuple of cities names that need to
                    be removed from restaurant names.
    """
    result = ''.join([char for char in x.lower() if char not in special_chars])
    new_result = ''
    for char in result:
        for item in special_letters:
            if char == item[0]:
                char = item[1]
        new_result += char
    result = new_result
    for item in cities:
        if item in result:
            result = result.replace(item, "")
    splitted_result = result.split()
    li_to_remove = []
    for word in splitted_result:
        if word in common_words:
            li_to_remove.append(word)
    for item in li_to_remove:
        splitted_result.remove(item)
    result = ' '.join(splitted_result)
    result = result.replace("  ", " ")
    result = result.replace("   ", " ")
    result.strip()
    return result


# Restaurant addresses cleaning
def address_cleaning(x, special_chars, special_letters, common_words):
    """
    It cleans the restaurant addresses by removing special
    characters, common words, by replacing special letters.
    Parameters:
        1. x = the address string that needs to be cleaned.
        2. special_chars = a list or tuple of special
                            characters that need to be removed.
        3. special_letters = a list or tuple of special letters
                                that need to be replaced with
                                normal letters.
        4. common_words = a list or tuple of common address words
                            that need to be removed from the address.
    """
    result = ''.join([char for char in x.lower() if char not in special_chars])
    splitted_result = result.split()
    li_to_remove = []
    for word in splitted_result:
        if word in common_words:
            li_to_remove.append(word)
    for item in li_to_remove:
        splitted_result.remove(item)
    result = ' '.join(splitted_result)
    new_result = ''
    for char in result:
        for item in special_letters:
            if char == item[0]:
                char = item[1]
        new_result += char
    result = new_result
    result = result.replace("   ", " ")
    result = result.replace("  ", " ")
    result.strip()
    return result


# Removing the city and zip from addresses
# def address_remove_cityandzip(x):
#    """
#    It removes the city and zip code from addresses if this
#    information is found at the end of the address after a ','.
#    """
#    splitted_x = x.split(",")[:-1]
#    return ' '.join(splitted_x)


# Removing other numbers from address like sector or bloc numbers
def address_remove_unecessary_numbers(x, li):
    """
    The function takes in an address and a list of words (not the
    street number words) that are usually followed by numbers.
    It removes these numbers from the address, leaving only the street
    number value so that it can be extracted easily afterwards.
    Parameters:
        1. x = the address string.
        2. li = the list or tuple of words other than street number
                that are usually followed by numbers.
    """
    x = x.replace(".", " ")
    x = x.replace("  ", " ")
    x = x.replace("   ", " ")
    list_x = x.lower().split()
    for item in li:
        if item in x.lower().split():
            index = list_x.index(item)
            if len(list_x) >= (index + 2):
                list_x.pop(index + 1)
    return ' '.join(list_x)


# Extracting the street number from addresses
def address_extract_street_no(x):
    """
    It exracts the street number form an address already cleaned
    of redundant numbers, of special characters etc.
    It extracts the last number from the address assuming that
    the street number is the last number remaining in the address
    after the address cleaning.
    Parameters:
        1. x = address string
    """
    list_of_digits = [[i for i in item if i.isdigit()] for item in x.split()]
    new_list = []
    if len(list_of_digits) > 0:
        for item in list_of_digits:
            if len(item) >= 1:
                new_list.append(item)
    else:
        return ''
    if len(new_list) > 1:
        return ''.join(new_list[-1])  # it joins and retrieves the last number in the address
    elif len(new_list) == 1:
        return ''.join(new_list[0])
    else:
        return ''


# Address processing function
def process_address(csv, x):
    x = change_address_nan(x)
    x = address_remove_unecessary_numbers(x, words_followed_by_numbers_tuple)
    x = address_cleaning(x,
                         special_chars_tuple,
                         special_letters_tuple,
                         common_address_words_tuple)
    return x


# Check if a name of a restaurant is equal or almost equal to
# the name of another restaurant from another data frame
def check_name(initial_name, comparison_name):
    """
    Checks if a restaurant name is equal or almost equal to
    another restaurant name.
    It takes in the following parameters:
        1. initial_name = the name which needs to be compared. It
                            is a list or a tuple of the name already
                            split into words.
        2. comparison_name = the name to compare with. It is a
                            list or a tuple of the name already
                            split into words.
    """
    if len(initial_name) > 0 and len(comparison_name) > 0:
        if ' '.join(initial_name) == ' '.join(comparison_name):
            return True
        elif ''.join(initial_name) == ''.join(comparison_name):
            return True
        elif ''.join(initial_name) in ''.join(comparison_name):
            return True
        elif ''.join(comparison_name) in ''.join(initial_name):
            return True
        elif initial_name[0] == comparison_name[0]:
            return True
        elif len(initial_name) > 3:
            if (str(initial_name[0]) in ' '.join(comparison_name)) and (
                    str(initial_name[1]) in ' '.join(comparison_name)) and (
                    str(initial_name[2]) in ' '.join(comparison_name)):
                return True
            elif ' '.join(initial_name[0:2]) in ' '.join(comparison_name):
                return True
            elif (str(initial_name[0]) in ' '.join(comparison_name)) and (
                    str(initial_name[2]) in ' '.join(comparison_name)) and (
                    str(initial_name[3]) in ' '.join(comparison_name)):
                return True
            elif ' '.join(initial_name) in ' '.join(comparison_name):
                return True
            elif ' '.join(comparison_name) in ' '.join(initial_name):
                return True
            elif ''.join(initial_name) in ''.join(comparison_name):
                return True
            elif ''.join(comparison_name) in ''.join(initial_name):
                return True
            else:
                return False
        elif len(initial_name) == 3:
            if (str(initial_name[0]) in ' '.join(comparison_name)) and (
                    str(initial_name[1]) in ' '.join(comparison_name)):
                return True
            elif ' '.join(initial_name[0:2]) in ' '.join(comparison_name):
                return True
            elif (str(initial_name[0]) in ' '.join(comparison_name)) and (
                    str(initial_name[2]) in ' '.join(comparison_name)):
                return True
            elif ' '.join(initial_name) in ' '.join(comparison_name):
                return True
            elif ' '.join(comparison_name) in ' '.join(initial_name):
                return True
            elif ''.join(initial_name) in ''.join(comparison_name):
                return True
            elif ''.join(comparison_name) in ''.join(initial_name):
                return True
            else:
                return False
        elif len(initial_name) == 2:
            if (str(initial_name[0]) in ' '.join(comparison_name)) and (
                    str(initial_name[1]) in ' '.join(comparison_name)):
                return True
            elif ' '.join(initial_name) in ' '.join(comparison_name):
                return True
            elif ' '.join(comparison_name) in ' '.join(initial_name):
                return True
            elif ''.join(initial_name) in ''.join(comparison_name):
                return True
            elif ''.join(comparison_name) in ''.join(initial_name):
                return True
            else:
                return False
        elif len(initial_name) == 1:
            if str(initial_name[0]) in ' '.join(comparison_name):
                return True
            elif ' '.join(comparison_name) in ' '.join(initial_name):
                return True
            elif ''.join(initial_name) in ''.join(comparison_name):
                return True
            elif ''.join(comparison_name) in ''.join(initial_name):
                return True
            else:
                return False
    else:
        return False


# Check if an address from a restaurant is equal or almost equal
# to another restaurant address from another data frame
def check_address(initial_address, comparison_address):
    """
    Checks if an address from a restaurant is equal or almost equal to
    another address.
    It takes in the following parameters:
        1. initial_address = address which needs to be compared. It
                            is a list or a tuple of the address already
                            split into words.
        2. comparison_address = the address to compare with. It is a
                                list or a tuple of the address already
                                split into words.
    """
    if len(initial_address) >= 1 and len(' '.join(comparison_address)) >= 1:
        if ' '.join(initial_address) == ' '.join(comparison_address):
            return True
        elif ' '.join(initial_address) in ' '.join(comparison_address):
            return True
        elif ' '.join(comparison_address) in ' '.join(initial_address):
            return True
        elif len(initial_address) > 3:
            if (initial_address[0] in ' '.join(comparison_address)) and (
                    initial_address[1] in ' '.join(comparison_address)) and (
                    initial_address[2] in ' '.join(comparison_address)):
                return True
            elif (initial_address[0] in ' '.join(comparison_address)) and (
                    initial_address[2] in ' '.join(comparison_address)) and (
                    initial_address[3] in ' '.join(comparison_address)):
                return True
            elif (initial_address[1] in ' '.join(comparison_address)) and (
                    initial_address[2] in ' '.join(comparison_address)) and (
                    initial_address[3] in ' '.join(comparison_address)):
                return True
            elif (initial_address[1] in ' '.join(comparison_address)) and (
                    initial_address[3] in ' '.join(comparison_address)):
                return True
            elif (initial_address[2] in ' '.join(comparison_address)) and (
                    initial_address[3] in ' '.join(comparison_address)):
                return True
            else:
                return False
        elif len(initial_address) == 3:
            if (initial_address[0] in ' '.join(comparison_address)) and (
                    initial_address[1] in ' '.join(comparison_address)):
                return True
            elif (initial_address[1] in ' '.join(comparison_address)) and (
                    initial_address[2] in ' '.join(comparison_address)):
                return True
            elif (initial_address[0] in ' '.join(comparison_address)) and (
                    initial_address[2] in ' '.join(comparison_address)):
                return True
            else:
                return False
        elif len(initial_address) == 2:
            if (initial_address[0] in ' '.join(comparison_address)) and (
                    initial_address[1] in ' '.join(comparison_address)):
                return True
            else:
                return False
        else:
            if ' '.join(initial_address) in ' '.join(comparison_address):
                return True
            else:
                return False
    else:
        return False


# It compares restaurants from a data frame by name and address with
# restaurants from another data frame. If it finds a match by words
# in name and by words in address, then it changes the restaurant name
# with the value of the compared restaurant name.
def finding_common_rest_names(initial_data, comparison_data):
    """
    It compares restaurants from a data base by name and address with
    restaurants from another data base.
    It takes in the following parameters:
        1. initial_data = a tuple or a list containing rows of the
                        restaurants data to be compared.
                        Each row needs to contain the following in
                        the same order:
                            a. restaurant name as a string
                            b. restaurant name as a list/tuple of words
                            c. restaurant address as a list/tuple of words
                            d. restaurant city as string
                            e. restaurant street number as str.
                            f. restaurant key
                            g. unique_rest_key
                            h. changed
        2. comparison_data = a tuple or a list containing rows of the
                        restaurants data the initial data will
                        be compared with.
                        Each row needs to contain the following in
                        the same order:
                            a. restaurant name as a string
                            b. restaurant name as a list/tuple of words
                            c. restaurant address as a list/tuple of words
                            d. restaurant city as string
                            e. restaurant street number as str.
                            f. restaurant key
                            g. unique_rest_key
    """
    results = []
    for i in initial_data:
        i_name = i[0]
        i_city = i[3]
        i_street_number = i[4]
        i_splitted_address = i[2]
        i_splitted_name = i[1]
        i_key = i[5]
        i_unique_key = i[6]
        i_changed = i[7]
        for item in comparison_data:
            item_name = item[0]
            item_city = item[3]
            item_street_number = item[4]
            item_splitted_address = item[2]
            item_splitted_name = item[1]
            item_key = item[5]
            if i_changed != "yes":
                if i_city == item_city:
                    if (i_street_number in item_splitted_address) or i_street_number == item_street_number:
                        checked_name = check_name(i_splitted_name, item_splitted_name)
                        if checked_name == True:
                            y = check_address(i_splitted_address, item_splitted_address)
                            if y == True:
                                i_name = item_name
                                i_key = item_key
                                i_changed = "yes"
                                print(i_name)
                            else:
                                continue
                        else:
                            continue
                else:
                    continue
        results.append((i_key, i_name, i_changed, i_unique_key))
    return results


# Adding the restaurant internal key in the reviews table
def add_rest_key_to_reviews(initial, comparison):
    """
    It compares the reviews data frame and the restaurants
    data frame on restaurant name, address and city and it
    returns the restaurants keys list to be added in the reviews
    data frame.
    Parameters:
        1. initial = a list or tuple of the reviews df following
                    information in the exact same order:
                        a. unique_id
        2. comparison = a list or tuple of the restaurants df
                        following information in the exact same order:
                            a. unique_id
                            b. rest_key
    """
    results = []
    for item in initial:
        item_rest_key = None
        for i in comparison:
            i_unique_id = str(i[0])
            i_rest_key = i[1]
            if str(item) in i_unique_id:
                item_rest_key = i_rest_key
        results.append(item_rest_key)
    return results


def retrieve_rest_info(rest_keys, comparison):
    """
    It retrieves the restaurant information (name, address, street_no, city etc.)
    in order to be able to add it to the grouped by restaurant key data frame.
    Parameters:
        1. rest_keys = restaurant keys int values for which the information is retrieved.
        2. comparison = a tuple or a list containing the information that needs to be
                        retrieved. It needs to contain the followings in the same exact
                        order:
                            a. "rest_key" - the restaurant key as an int
                            b. "name" - the name of the restaurant as a string
                            c. "city" - the address of the restaurant as a string
                            d. "address" - the cleaned restaurant name
                            e. "categories" - the cleaned restaurant address
                            f. "tazz_restaurant_page_href"- the address street no.
                            g. "fp_restaurant_page_href" - the restaurant categories
                            h. "rest_image" - the city of the restaurant
                            i. "unique_id" - the restaurant page href
                            j. "internal_address" - the restaurant image url.
                            k. "street_no"
                            l. "internal_name"
                            m. "tazz_delivery_fee"
                            n. "fp_delivery_fee"
                            o. "tazz_minimum_order"
                            p. "fp_minimum_order"

    """
    results = []
    for item in rest_keys:
        for i in comparison:
            i_key = i[0]
            i_name = i[1]
            i_city = i[2]
            i_address = i[3]
            i_categories = i[4]
            i_tazz_page = i[5]
            i_fp_page = i[6]
            i_image = i[7]
            i_unique_id = i[8]
            i_internal_address = i[9]
            i_street_no = i[10]
            i_internal_name = i[11]
            i_tazz_delivery_fee = i[12]
            i_fp_delivery_fee = i[13]
            i_tazz_minimum_order = i[14]
            i_fp_minimum_order = i[15]
            if item == i_key:
                results.append((i_key,
                                i_name,
                                i_city,
                                i_address,
                                i_categories,
                                i_tazz_page,
                                i_fp_page,
                                i_image,
                                i_unique_id,
                                i_internal_address,
                                i_street_no,
                                i_internal_name,
                                i_tazz_delivery_fee,
                                i_fp_delivery_fee,
                                i_tazz_minimum_order,
                                i_fp_minimum_order
                                ))
                break

    return results


def image_process(x):
    if pd.isnull(x):
        return x
    else:
        return x.split("?")[0]


# Gather up both tazz and fp restaurant page links for common restaurants
def gather_page_links(initial, comparison):
    results = []
    for i in initial:
        i_key = i[0]
        i_page = i[1]
        for item in comparison:
            item_key = item[0]
            item_page = item[1]
            if i_key == item_key:
                i_page = item_page
        results.append(i_page)
    return results


# Gather up both tazz and fp restaurant delivery fees for common restaurants
def gather_delivery_fees(initial, comparison):
    results = []
    for i in initial:
        i_key = i[0]
        i_fee = i[1]
        for item in comparison:
            item_key = item[0]
            item_fee = item[1]
            if i_key == item_key:
                i_fee = item_fee

        results.append(i_fee)
    return results


# Gather up both tazz and fp restaurant minimum order for common restaurants
def gather_minimum_order(initial, comparison):
    results = []
    for i in initial:
        i_key = i[0]
        i_fee = i[1]
        for item in comparison:
            item_key = item[0]
            item_fee = item[1]
            if i_key == item_key:
                i_fee = item_fee

        results.append(i_fee)
    return results


def process_rest_csv(csv, *args):
    df = pd.read_csv(csv)
    df["unique_id"] = df["name"] + df["city"] + df["address"] + df["source"]

    if "foodpanda" in csv:
        df_restaurants = df[fp_columns]
    elif "tazz" in csv:
        df_restaurants = df[tazz_columns]
    df_restaurants = group_rest(list(zip(df_restaurants["unique_id"].values, tuple(df_restaurants.iloc[:, :].values))))
    if "foodpanda" in csv:
        df_restaurants = pd.DataFrame(df_restaurants, columns=fp_columns)
    elif "tazz" in csv:
        df_restaurants = pd.DataFrame(df_restaurants, columns=tazz_columns)
    # Set the keys to the fp_restaurants data frame
    if args:
        df_restaurants["rest_key"] = set_keys(args[0] + 1, len(df_restaurants))
    else:
        df_restaurants["rest_key"] = set_keys(1, len(df_restaurants))
    # Updating the restaurants page links
    if "foodpanda" in csv:
        df_restaurants["fp_restaurant_page_href"] = "https://www.foodpanda.ro" + df_restaurants[
            "fp_restaurant_page_href"]

    # Updating restaurant images
    if "foodpanda" in csv:
        df_restaurants["rest_image"] = df_restaurants["rest_image"].apply(lambda x: image_process(x))

    # Updating the delivery_fee column values
    if "foodpanda" in csv:
        df_restaurants["fp_delivery_fee"] = df_restaurants["fp_delivery_fee"].apply(lambda x: change_delivery_fee(x))
        df_restaurants["fp_delivery_fee"] = df_restaurants["fp_delivery_fee"].apply(
            lambda x: ' '.join(x.split(" ")[1:]))
    elif "tazz" in csv:
        df_restaurants["tazz_delivery_fee"] = df_restaurants["tazz_delivery_fee"].apply(
            lambda x: change_delivery_fee(x))
        df_restaurants["tazz_delivery_fee"] = df_restaurants["tazz_delivery_fee"].apply(
            lambda x: ' '.join(x.split(" ")[1:]))

    # Updating the minimum_order column
    if "foodpanda" in csv:
        df_restaurants["fp_minimum_order"] = df_restaurants["fp_minimum_order"].apply(lambda x: change_minimum_order(x))
    elif "tazz" in csv:
        df_restaurants["tazz_minimum_order"] = df_restaurants["tazz_minimum_order"].apply(
            lambda x: change_minimum_order(x))

    # Transforming the reviews_no column to int
    df_restaurants["reviews_no"] = df_restaurants["reviews_no"].apply(lambda x: value_to_int(x))

    # Cleaning up the address
    df_restaurants["internal_address"] = df_restaurants["address"].apply(lambda x: process_address(csv, x))

    # Extracting the street number from the address
    df_restaurants["street_no"] = df_restaurants["internal_address"].apply(lambda x: address_extract_street_no(x))

    # Cleaning the restaurant names
    df_restaurants["internal_name"] = df_restaurants["name"].apply(lambda x: name_cleaning(x,
                                                                                           special_chars_tuple,
                                                                                           special_letters_tuple,
                                                                                           common_rest_words_tuple,
                                                                                           city_names_tuple))
    # Splitting the restaurant name and the address into separate words
    df_restaurants["splitted_internal_name"] = df_restaurants["internal_name"].apply(lambda x: x.split())
    df_restaurants["splitted_internal_address"] = df_restaurants["internal_address"].apply(lambda x: x.split())
    df_restaurants["changed"] = "no"
    if "foodpanda" in csv:
        df_restaurants["tazz_restaurant_page_href"] = None
    elif "tazz" in csv:
        df_restaurants["fp_restaurant_page_href"] = None
    if "foodpanda" in csv:
        df_restaurants["tazz_minimum_order"] = None

    elif "tazz" in csv:
        df_restaurants["fp_minimum_order"] = None

    if "foodpanda" in csv:
        df_restaurants["tazz_delivery_fee"] = None
    elif "tazz" in csv:
        df_restaurants["fp_delivery_fee"] = None
    return df_restaurants


def changing_common_rest(df1, df2):
    df1_changed_rest = finding_common_rest_names(tuple(df1[columns_forfinding_common_rest].values),
                                                 tuple(df2[columns_forfinding_common_rest].values))
    df1_changed_rest = pd.DataFrame(df1_changed_rest,
                                    columns=["rest_key",
                                             "name",
                                             "changed",
                                             "unique_key"])
    df1["rest_key"] = df1_changed_rest["rest_key"]
    df1["changed"] = df1_changed_rest["changed"]
    return df1


def process_review_date(df, source):
    if "foodpanda" in source:
        df["day"] = df["review_date"].apply(lambda x: x.split()[0])
        df["month"] = df["review_date"].apply(lambda x: x.split()[1])
        df["year"] = df["review_date"].apply(lambda x: x.split()[2])
        df["month"] = df["month"].apply(lambda x: replace_dayormonthstr(x, months_mapping))
        df["day"] = df["day"].apply(lambda x: replace_dayormonthstr(x, days_mapping))

        df["review_date"] = df["year"] + "-" + df["month"] + "-" + df["day"]
        df.drop(["day", "month", "year"], axis=1, inplace=True)
    elif "tazz" in source:
        df["day"] = df["review_date"].apply(lambda x: x.split(".")[0])
        df["month"] = df["review_date"].apply(lambda x: x.split(".")[1])
        df["year"] = df["review_date"].apply(lambda x: x.split(".")[2])

        df["review_date"] = df["year"] + "-" + df["month"] + "-" + df["day"]
        df.drop(["day", "month", "year"], axis=1, inplace=True)
    return df


def process_reviews_csv(csv, *args):
    df = pd.read_csv(csv)
    df["unique_id"] = df["name"] + df["city"] + df["address"] + df["source"]
    df_reviews = df[review_columns]
    df_reviews = df_reviews[pd.notnull(df_reviews["review_date"])]
    if "foodpanda" in csv:
        df_reviews = process_review_date(df_reviews, "foodpanda")
    elif "tazz" in csv:
        df_reviews = process_review_date(df_reviews, "tazz")
    if "tazz" in csv:
        df_reviews["review_rating"] = df_reviews["review_rating"].apply(lambda x: x.replace(",", "."))
        df_reviews["review_rating"] = df_reviews["review_rating"].apply(float)
    return df_reviews


def final_reviews_processing(csv1, csv2, rest_df):
    df1 = process_reviews_csv(csv1)
    df2 = process_reviews_csv(csv2)
    final_reviews = pd.concat([df1, df2], axis=0)
    final_reviews["review_key"] = set_keys(1, len(final_reviews))
    # Adding the restaurant keys to the reviews table
    final_reviews["rest_key"] = add_rest_key_to_reviews(tuple(final_reviews["unique_id"].values),
                                                        tuple(rest_df[["unique_id", "rest_key"]].values))
    final_reviews = final_reviews[final_reviews_columns]
    return final_reviews


def final_restaurant_processing(csv1, csv2, *args):
    if "foodpanda" in csv1:
        df1 = process_rest_csv(csv1)
        df2 = process_rest_csv(csv2, len(df1))
        df2 = changing_common_rest(df2, df1)
    elif "tazz" in csv1:
        df1 = process_rest_csv(csv2)
        df2 = process_rest_csv(csv1, len(df1))
        df2 = changing_common_rest(df2, df1)
    if args:
        df3 = process_rest_csv(args[0], len(df2))
        df3 = changing_common_rest(df3, df2)
    df1["tazz_restaurant_page_href"] = gather_page_links(tuple(df1[["rest_key", "tazz_restaurant_page_href"]].values),
                                                         tuple(df2[["rest_key", "tazz_restaurant_page_href"]].values))
    df2["fp_restaurant_page_href"] = gather_page_links(tuple(df2[["rest_key", "fp_restaurant_page_href"]].values),
                                                       tuple(df1[["rest_key", "fp_restaurant_page_href"]].values))
    df1["unique_id"] = group_unique_ids(tuple(df1[["rest_key", "unique_id"]].values),
                                        tuple(df2[["rest_key", "unique_id"]].values))
    df2["unique_id"] = group_unique_ids(tuple(df2[["rest_key", "unique_id"]].values),
                                        tuple(df1[["rest_key", "unique_id"]].values))

    df2["fp_delivery_fee"] = gather_delivery_fees(tuple(df2[["rest_key", "fp_delivery_fee"]].values),
                                                  tuple(df1[["rest_key", "fp_delivery_fee"]].values))
    df1["tazz_delivery_fee"] = gather_delivery_fees(tuple(df1[["rest_key", "tazz_delivery_fee"]].values),
                                                    tuple(df2[["rest_key", "tazz_delivery_fee"]].values))
    df1["tazz_minimum_order"] = gather_minimum_order(tuple(df1[["rest_key", "tazz_minimum_order"]].values),
                                                     tuple(df2[["rest_key", "tazz_minimum_order"]].values))

    df2["fp_minimum_order"] = gather_minimum_order(tuple(df2[["rest_key", "fp_minimum_order"]].values),
                                                   tuple(df1[["rest_key", "fp_minimum_order"]].values))
    df1 = df1[rest_columns_before_concatenation]
    df2 = df2[rest_columns_before_concatenation]
    concatenated_rest = pd.concat([df1, df2], axis=0)
    concatenated_rest["reviews_total"] = concatenated_rest[["restaurant_rating", "reviews_no"]].apply(
        lambda x: sum_of_reviews(*x), axis=1)
    grouped_by_key_rest = concatenated_rest.groupby("rest_key").sum()
    grouped_by_key_rest["restaurant_rating"] = round(
        grouped_by_key_rest["reviews_total"] / grouped_by_key_rest["reviews_no"], 1)
    grouped_by_key_rest.reset_index(inplace=True)
    restaurant_info = retrieve_rest_info(grouped_by_key_rest["rest_key"].values,
                                         tuple(concatenated_rest[restaurant_merging_columns].values))
    rest_info_df = pd.DataFrame(restaurant_info, columns=restaurant_merging_columns)
    final_restaurants = pd.merge(rest_info_df, grouped_by_key_rest, on="rest_key")
    final_restaurants["img"] = image_titles(final_restaurants["rest_image"].values)
    final_restaurants["city"] = final_restaurants["city"].apply(capitalize_city)

    final_restaurants["rest_key"] = set_keys(1, len(final_restaurants))

    return final_restaurants


def write_restaurants_unique_id_csv(restaurants):
    with open(os.path.join(dirname(dirname(__file__)), "media/csv/final_restaurants_unique_id.csv"), "w",
              encoding="utf-8", newline="") as file:
        headers = ["unique_id"]
        csv_writer = DictWriter(file, fieldnames=headers)
        csv_writer.writeheader()
        for rest in restaurants:
            csv_writer.writerow(rest)


def new_images_downloader(df, existent_csv):
    existent_unique_ids = pd.read_csv(existent_csv)
    for item in df[["unique_id", "rest_image"]].values:
        result = []
        for i in existent_unique_ids.values:
            if item[0] not in i:
                result.append(True)
            else:
                result.append(False)
        if all(result):
            img.download(item[1], "media/restaurants/images")


def delete_reviews_table():
    conn = psg.connect(
        "dbname = 'restaurants' user = 'postgres' password = 'postgrespass' host = 'localhost' port = '5432'")
    c = conn.cursor()
    c.execute("DELETE FROM restaurants_review")
    conn.commit()
    conn.close()


def delete_restaurants_table():
    conn = psg.connect(
        "dbname = 'restaurants' user = 'postgres' password = 'postgrespass' host = 'localhost' port = '5432'")
    c = conn.cursor()
    c.execute("DELETE FROM restaurants_restaurant")
    conn.commit()
    conn.close()


def write_unique_id(restaurants):
    values = []
    for item in restaurants["unique_id"].values:
        values.append({"unique_id": item})
    return values


def bulk_insert_into_restaurants_table(data):
    conn = psg.connect(
        "dbname = 'restaurants' user = 'postgres' password = 'postgrespass' host = 'localhost' port = '5432'")
    c = conn.cursor()
    c.executemany(
        "INSERT INTO restaurants_restaurant VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);",
        tuple(data))
    conn.commit()
    conn.close()


def bulk_insert_into_reviews_table(data):
    conn = psg.connect(
        "dbname = 'restaurants' user = 'postgres' password = 'postgrespass' host = 'localhost' port = '5432'")
    c = conn.cursor()
    c.executemany("INSERT INTO restaurants_review VALUES (%s, %s, %s, %s, %s, %s, %s, %s);",
                  tuple(data))
    conn.commit()
    conn.close()


def update_data():
    tazz_reviews = tazz.get_reviews_info(tazz.url, tazz.cities, tazz.category)
    tazz.write_restaurants_info_to_csv(tazz_reviews)
    fp_reviews = fp.get_reviews_info(fp.base_url, fp.base_search_url, fp.cities)
    fp.write_restaurants_info_to_csv(fp_reviews)
    print("process restaurants")
    final_restaurants = final_restaurant_processing("../media/csvs/foodpanda.csv", "../media/csvs/tazz.csv")
    print("download_images")
    new_images_downloader(final_restaurants, "final_restaurants_unique_id.csv")
    print("process reviews")
    final_reviews = final_reviews_processing("../media/csvs/tazz.csv", "../media/csvs/foodpanda.csv", final_restaurants)
    values = write_unique_id(final_restaurants)
    write_restaurants_unique_id_csv(values)
    print("delete reviews table")
    delete_reviews_table()
    print("delete restaurants table")
    delete_restaurants_table()
    print("insert data into tables")
    bulk_insert_into_restaurants_table(final_restaurants.values)
    bulk_insert_into_reviews_table(final_reviews.values)


# def update_data():
#     tazz_reviews = tazz.get_reviews_info(tazz.url, tazz.cities, tazz.category)
#     tazz.write_restaurants_info_to_csv(tazz_reviews)
#     fp_reviews = fp.get_reviews_info(fp.base_url, fp.base_search_url, fp.cities)
#     fp.write_restaurants_info_to_csv(fp_reviews)
#     print("process restaurants")
#     final_restaurants = final_restaurant_processing("../media/csvs/foodpanda.csv", "../media/csvs/tazz.csv")
#     print("download_images")
#     new_images_downloader(final_restaurants, "final_restaurants_unique_id.csv")
#     print("process reviews")
#     final_reviews = final_reviews_processing("../media/csvs/tazz.csv", "../media/csvs/foodpanda.csv", final_restaurants)
#     values = write_unique_id(final_restaurants)
#     write_restaurants_unique_id_csv(values)
#     print("delete reviews table")
#     delete_reviews_table()
#     print("delete restaurants table")
#     delete_restaurants_table()
#     print("insert data into tables")
#     bulk_insert_into_restaurants_table(final_restaurants.values)
#     bulk_insert_into_reviews_table(final_reviews.values)


def initial_download():
    tazz_reviews = tazz.get_reviews_info(tazz.url, tazz.cities, tazz.category)
    tazz.write_restaurants_info_to_csv(tazz_reviews)
    fp_reviews = fp.get_reviews_info(fp.base_url, fp.base_search_url, fp.cities)
    fp.write_restaurants_info_to_csv(fp_reviews)
    final_restaurants = final_restaurant_processing("../media/csvs/foodpanda.csv", "../media/csvs/tazz.csv")
    img.bulk_download(final_restaurants["rest_image"].values, "media/restaurants/images")
    final_reviews = final_reviews_processing("../media/csvs/tazz.csv", "../media/csvs/foodpanda.csv", final_restaurants)
    values = write_unique_id(final_restaurants)
    write_restaurants_unique_id_csv(values)
    delete_reviews_table()
    print("delete restaurants table")
    delete_restaurants_table()
    bulk_insert_into_restaurants_table(final_restaurants.values)
    bulk_insert_into_reviews_table(final_reviews.values)


# def initial_download1():
#     # tazz_reviews = tazz.get_reviews_info(tazz.url, tazz.cities, tazz.category)
#     # tazz.write_restaurants_info_to_csv(tazz_reviews)
#     # fp_reviews = fp.get_reviews_info(fp.base_url, fp.base_search_url, fp.cities)
#     # fp.write_restaurants_info_to_csv(fp_reviews)
#     final_restaurants = final_restaurant_processing("../media/csvs/foodpanda.csv", "../media/csvs/tazz.csv")
#     img.bulk_download(final_restaurants["rest_image"].values, "media/restaurants/images")
#     final_reviews = final_reviews_processing("../media/csvs/tazz.csv", "../media/csvs/foodpanda.csv", final_restaurants)
#     values = write_unique_id(final_restaurants)
#     write_restaurants_unique_id_csv(values)
#     delete_reviews_table()
#     print("delete restaurants table")
#     delete_restaurants_table()
#     bulk_insert_into_restaurants_table(final_restaurants.values)
#     bulk_insert_into_reviews_table(final_reviews.values)


# Data to be used to clean the restaurant names and addresses
special_chars_tuple = ("#", ")", "(", "'", "'", "!", "\"", "’", "`", "/", "@", "`")
special_letters_tuple = (("ε", "e"), ("î", "i"), ("-", " "), (".", " "),
                         (",", " "), ("ç", "c"), ("ô", "o"), ("ș", "s"),
                         ("ă", "a"), ("_", " "), ("–", " "), ("&", " "),
                         ("ț", "t"), ("ö", "o"), ("é", "e"), ("®", ""),
                         ("â", "a"), ("ş", "s"), ("ő", "o"), ("κ", "k"),
                         ("â", "a"), ("á", "a"), ("ţ", "t"), ("ó", "o"),
                         ("á", "a"), ("ê", "e"), ("ü", "u"))
common_address_words_tuple = ("b-dul", "strada", "aleea", "bd", "bdul",
                              "bdul.", "bulevardul", "nr", "intrarea",
                              "prelungirea", "divizia", "sos", "sos", "bloc", "sc",
                              "etaj", "bl.", "sc.", "et", "bl", "et.", "sectorul",
                              "scara", "halelor", "sc", "nr.", "sector", "sect", "sect.",
                              "soseaua", "splaiul", "camera", "stada", "str.", "str",
                              "ap", "apartament", "spatiul", "parter", "calea")
words_followed_by_numbers_tuple = ("sector", "camera", "sectorul", "halelor", "sect.",
                                   "etaj", "et", "ap", "apt", "apartament", "ap.",
                                   "bloc", "bl", "divizia", "bl.", "sector", "et.",
                                   "scara", "sc.", "sc", "parter", "spatiul")
city_names_tuple = ("bucuresti", "cluj-napoca", "timisoara",
                    "iasi", "brasov", "oradea", "constanta",
                    "arad", "sibiu", "galati", "pitesti",
                    "craiova", "ploiesti", "baia-mare",
                    "baia mare", "cluj napoca", "targu mures",
                    "buzau", "braila", "bacau", "targu-mures",
                    "suceava", "roman", "alba-iulia", "alba iulia",
                    "resita", "botosani", "deva")
common_rest_words_tuple = ("restaurant", "catering", "delivery", "taverna",
                           "trattoria", "restaurantul", "pizza",
                           "pizzeria", "la", "the")

# Months data
months_mapping = (("ian.", "01"),
                  ("feb.", "02"),
                  ("mar.", "03"),
                  ("apr.", "04"),
                  ("mai", "05"),
                  ("iun.", "06"),
                  ("iul.", "07"),
                  ("aug.", "08"),
                  ("sept.", "09"),
                  ("oct.", "10"),
                  ("nov.", "11"),
                  ("dec.", "12"))

# Days data
days_mapping = (("1", "01"),
                ("2", "02"),
                ("3", "03"),
                ("4", "04"),
                ("5", "05"),
                ("6", "06"),
                ("7", "07"),
                ("8", "08"),
                ("9", "09"))

# Data frames restaurant columns
fp_columns = ["name",
              "restaurant_rating",
              "reviews_no",
              "city",
              "address",
              "categories",
              "source",
              "fp_minimum_order",
              "fp_delivery_fee",
              "fp_restaurant_page_href",
              "rest_image",
              "unique_id"]

tazz_columns = ["name",
                "restaurant_rating",
                "reviews_no",
                "city",
                "address",
                "categories",
                "source",
                "tazz_minimum_order",
                "tazz_delivery_fee",
                "tazz_restaurant_page_href",
                "rest_image",
                "unique_id"]

rest_columns_before_concatenation = ["name",
                                     "restaurant_rating",
                                     "reviews_no",
                                     "city",
                                     "address",
                                     "categories",
                                     "source",
                                     "tazz_restaurant_page_href",
                                     "fp_restaurant_page_href",
                                     "rest_image",
                                     "unique_id",
                                     "rest_key",
                                     "internal_address",
                                     "street_no",
                                     "internal_name",
                                     "tazz_delivery_fee",
                                     "fp_delivery_fee",
                                     "tazz_minimum_order",
                                     "fp_minimum_order"
                                     ]

# Finding common restaurants comparison columns
columns_forfinding_common_rest = ["internal_name",
                                  "splitted_internal_name",
                                  "splitted_internal_address",
                                  "city",
                                  "street_no",
                                  "rest_key",
                                  "unique_id",
                                  "changed"]
restaurant_merging_columns = ["rest_key",
                              "name",
                              "city",
                              "address",
                              "categories",
                              "tazz_restaurant_page_href",
                              "fp_restaurant_page_href",
                              "rest_image",
                              "unique_id",
                              "internal_address",
                              "street_no",
                              "internal_name",
                              "tazz_delivery_fee",
                              "fp_delivery_fee",
                              "tazz_minimum_order",
                              "fp_minimum_order"]
review_columns = ["review",
                  "review_date",
                  "review_rating",
                  "author",
                  "source",
                  "unique_id"
                  ]
final_reviews_columns = ["review_key",
                         "review",
                         "review_date",
                         "review_rating",
                         "author",
                         "source",
                         "unique_id",
                         "rest_key"
                         ]

# Platforms
platforms = ["foodpanda", "tazz"]
