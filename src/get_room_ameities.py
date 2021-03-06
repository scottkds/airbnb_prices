import pandas as pd
from airbnb_lib import get_price_ranges, setup_webdriver, get_page, format_url, page_offset, number_of_stays_page_bottom
from airbnb_lib import get_listings_from_json, get_listings_data
import airbnb_page_components_lib as pc
from datetime import datetime, timedelta
from collections import defaultdict
import time
import re
import json
import pickle
import sys
import gc
import pdb

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

    with open('room_data.json', 'w') as f:
        try:
            f.write(json.dumps(room_data))
        except Exception as e:
            pdb.set_trace()
    f.close()

    with open('amenities_data.json', 'w') as f:
        f.write(json.dumps(amenities_data))
    f.close()

    with open('json_data.json', 'w') as f:
        f.write(json.dumps(json_data))
    f.close()
    return True


BASE_URL = pc.BASE_URL
START_DATE = datetime(2020, 10, 1)
END_DATE = datetime(2020, 10, 5)

nprops = nbr_props()
plus_rooms = plus_room_count()
room_data = defaultdict(list)
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

driver.close()
print(price_ranges)
#exit()

for pr in price_ranges[10:]:
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
        if number_stays_bp[0] >= number_stays_bp[2]:
            break
        stays_json = get_listings_from_json(soup)
        json_data = get_listings_data(stays_json, ['id', 'lat', 'lng'], json_data)
        stays = pc.get_page_stays_list(soup)
        for stay in stays:
            load_stay = True
            link = 'https://www.airbnb.com' + pc.relative_link(stay)
            room_id = pc.get_id(link)
            if room_id > 0:
                print('Number of properties:', next(nprops))
                print(link)
                room_data['id'].append(room_id)
                stay_soup = get_page(link, driver, delay=6)

                # Airbnb seems to load the various aspects of a page individually.
                # The following try/except block will try to scrape a page and if
                # if fails it will reload the page with a longer delay. If that 
                # fails the stay will be skipped.
                try:
                    price, stars, reviews, cleaning_fee, long_stay_discount, superhost = pc.get_price_summary_info(stay_soup)
                    guests, bedrooms, beds, baths = pc.get_rooms(stay_soup)
                except Exception as e:
                    print('Page reloading due to exception', e)
                    stay_soup = get_page(link, driver, delay=15)
                    try:
                        price, stars, reviews, cleaning_fee, long_stay_discount, superhost = pc.get_price_summary_info(stay_soup)
                        guests, bedrooms, beds, baths = pc.get_rooms(stay_soup)
                    except:
                        load_stay = False
                if load_stay:
                    room_data['price'].append(price)
                    room_data['stars'].append(stars)
                    room_data['reviews'].append(reviews)
                    room_data['cleaning_fee'].append(cleaning_fee)
                    room_data['long_stay_discount'].append(long_stay_discount)
                    room_data['superhost'].append(superhost)
                    room_data['guests'].append(guests)
                    room_data['bedrooms'].append(bedrooms)
                    room_data['beds'].append(beds)
                    room_data['baths'].append(baths)
                    amenities_element = pc.get_amenities_elem(driver)
                    amenities_element.click()
                    time.sleep(2)
                    amenities = pc.get_amenities(driver.page_source)
                    amenities_data[room_id] = amenities
                driver.back()
                driver.back()
            else:
                print('Skipping "/plus room number:', next(plus_rooms))
        dump_data()
        driver.close()
        gc.collect()
        #pdb.set_trace()


print(price_ranges)

driver.close()
