import pandas as pd
from airbnb_lib import get_price_ranges, setup_webdriver, get_page, format_url, page_offset, number_of_stays_page_bottom
from airbnb_lib import get_listings_from_json, get_listings_data
import airbnb_page_components_lib as pc
from datetime import datetime, timedelta
from collections import defaultdict
from find_key import find_key
import time
import re
import json
import pickle
import sys
import gc
import pdb

#==============================================================================
# TODO
#==============================================================================
# 1. Choose elements to gather.
#   a. --Stars
#   b. --Nbr bedrooms
#   c. --Nbr beds
#   d. --Nbr baths
#   e. --Price
#   f. --Cleaning fee
#   g. --Discount
#   h. --Amenitites
#   i. --Id
#   j. --Latitude
#   k. --Longitude
# 2. Aggregate data into a DataFrame
# 3. Calculate distances to Bogota tourist attractions
# 4. Model Linear Regression, Ridge, Lasso, random forest, SVM regressor
# 5. Visualizations
# 6. Publication

def nbr_props():
    i = 1
    while True:
        yield i
        i += 1

def plus_room_count():
    i = 1
    while True:
        yield i
        i += 1

def dump_data():

    with open('json_data.json', 'w') as f:
        f.write(json.dumps(json_data))
    f.close()
    return True


BASE_URL = pc.BASE_URL
START_DATE = datetime(2020, 10, 1)
END_DATE = datetime(2020, 10, 5)

nprops = nbr_props()
plus_rooms = plus_room_count()
json_data = defaultdict(list)

driver = setup_webdriver(width=1100, height=1020)

if '--use-pickle' in sys.argv:
    with open('price_range.pkl', 'rb') as f:
        price_ranges = pickle.load(f)
    f.close()
else:
    price_ranges = get_price_ranges(BASE_URL, driver, START_DATE, END_DATE, 0, 50)

    with open('price_range.pkl', 'wb') as f:
        pickle.dump(price_ranges, f)
    f.close()

json_fields = ['id', 
               'price',
               'rate',
               'bedrooms', 
               'beds', 
               'bathrooms', 
               'personCapacity', 
               'reviewsCount', 
               'isSuperhost', 
               'avgRating', 
               'amenityIds', 
               'lat', 
               'lng']

driver.close()
print(price_ranges)
#exit()

for pr in price_ranges[:]:
    offset_gen = page_offset()
    nbr_pages = pr[0] // 20 + 1
    price_min = pr[1]
    price_max = pr[2]
    for page in range(nbr_pages):

        try:
            driver = setup_webdriver(width=1100, height=1020)
        except OSError:
            time.sleep(60)
            try:
                driver = setup_webdriver(width=1100, height=1020)
            except Exception as e:
                raise e

        url = format_url(BASE_URL, 
                         next(offset_gen), 
                         start_date=START_DATE, 
                         end_date=END_DATE,
                         min_price=price_min,
                         max_price=price_max)
        try:
            soup = get_page(url, driver, delay=15)
        except:
            driver.close()
            driver = setup_webdriver(width=1100, height=1020)
            try:
                soup = get_page(url, driver, delay=15)
            except:
                break

        number_stays_bp = number_of_stays_page_bottom(soup)
        print(number_stays_bp)
        if number_stays_bp[1] >= number_stays_bp[2]:
            break
        try:
            stays_json = get_listings_from_json(soup)
        except IndexError:
            time.sleep(30)
            try:
                stays_json = get_listings_from_json(soup)
            except Exception as e:
                raise e
        json_data = get_listings_data(stays_json, json_fields, json_data)
        stays = pc.get_page_stays_list(soup)
        dump_data()
        driver.close()
        gc.collect()
        #pdb.set_trace()


print(price_ranges)

driver.close()
