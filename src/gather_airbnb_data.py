import pandas as pd
from airbnb_lib import get_price_ranges, setup_webdriver, get_page, format_url, page_offset
from airbnb_lib import get_listings_from_json, get_listings_data
import airbnb_page_components_lib as pc
from datetime import datetime, timedelta
from collections import defaultdict
import re
import pickle
import sys

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
#   j. Latitude
#   k. Longitude
# 2. Aggregate data into a DataFrame
# 3. Calculate distances to Bogota tourist attractions
# 4. Model Linear Regression, Ridge, Lasso, random forest, SVM regressor
# 5. Visualizations
# 6. Publication


BASE_URL = pc.BASE_URL
START_DATE = datetime(2020, 10, 1)
END_DATE = datetime(2020, 10, 5)

room_data = {}
amenities_data = {}
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



for pr in price_ranges:
    offset_gen = page_offset()
    nbr_pages = pr[0] // 20 + 1
    price_min = pr[1]
    price_max = pr[2]
    for page in range(nbr_pages):
        url = format_url(BASE_URL, 
                         next(offset_gen), 
                         start_date=START_DATE, 
                         end_date=END_DATE,
                         min_price=price_min,
                         max_price=price_max)
        soup = get_page(url, driver, delay=15)
        stays_json = get_listings_from_json(soup)
        json_data = get_listings_data(stays_json, ['id', 'lat', 'lng'], json_data)
        stays = pc.get_page_stays_list(soup)
        for stay in stays:
            link = 'https://www.airbnb.com' + pc.relative_link(stay)
            room_id = pc.get_id(link)
            price, stars, reviews, cleaning_fee, long_stay_discount, superhost = pc.get_price_summary_info(soup)
            guests, bedrooms, beds, baths = pc.get_rooms(soup)
            amenities_element = pc.get_amenities_elem(driver)
            amenities_element.click()
            amenities_soup = bs4.BeautifulSoup(self.driver.page_source, features='html.parser')
            amenitites = pc.get_amenities(amenities_soup)
            amenities_data[room_id] = amenities
            driver.back()




print(price_ranges)

driver.close()
