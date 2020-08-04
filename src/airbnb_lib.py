# Imports
import pandas as pd
import selenium
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import bs4
from bs4 import BeautifulSoup
import re
import json
import time
from collections import defaultdict
from datetime import datetime, timedelta
from collections import defaultdict
from math import acos, sin, cos
from find_key import find_key
import unittest
import pdb

START_DATE = datetime.now() + timedelta(days=90)
END_DATE = datetime.now() + timedelta(days=93)
# START_DATE = datetime.now() + timedelta(days=90)
# END_DATE = datetime.now() + timedelta(days=93)
BASE_URL = 'https://www.airbnb.com/s/Bogota--Colombia/homes?tab_id=home_tab&refinement_paths%5B%5D=%2Fhomes&place_id=ChIJKcumLf2bP44RFDmjIFVjnSM&source=structured_search_input_header&search_type=pagination&federated_search_session_id=03d88384-9106-466f-a2f1-4150e425ada3&query=Bogota%2C%20Colombia&checkin={start_date}&checkout={end_date}&price_min={min_price}&price_max={max_price}&room_types%5B%5D=Entire%20home%2Fapt&section_offset=2&items_offset={offset}'

def format_url(url, offset=0, start_date=datetime(2021, 1, 1), end_date=datetime(2021, 1, 4), min_price=0, max_price=20):
    """Accepts a url and a price_range tuple and will format the url with the information
    in the tuple. The offset will be filled with the '{}' string and the offset value will be
    formated when paging through the Airbnb listings."""
    
    formatted_start_date = start_date.strftime('%Y-%m-%d')
    formatted_end_date = end_date.strftime('%Y-%m-%d')

    return url.format(start_date=formatted_start_date, end_date=formatted_end_date, min_price=min_price, max_price=max_price, offset=offset)


def setup_webdriver(width=800, height=600):
    """Opens a chrome window and sets the size of the window. The webdriver object is returned."""
    # driver = selenium.webdriver.Firefox()
    driver = selenium.webdriver.Chrome()
    driver.set_window_size(width, height, windowHandle='current')
    time.sleep(1)
    return driver


def get_page(url, driver, delay=5):
    """Returns the BeautifulSoup object of the page source."""
    driver.get(url)
    time.sleep(delay)
    return BeautifulSoup(driver.page_source, features='html.parser')
    # return driver.page_source


def page_offset():
    """Generator that yields integers starting at zero and incrementing by 20 each time.
    This is used to page listing offsets."""
    n = 0
    while True:
        yield n
        n += 20

def find_room_count_for_range(base_url, driver, start_date, end_date, min_price=0, max_price=10):
    """Requests Airbnb listings and searches for the price range that yields the greatest number
    of stays that is less than 300. The price range is returned as a tuple. The function adds $20
    until it exceeds 299 stays. The function will do a binary search for the lowest price that will yield
    the greatest number of stays that is less than 300.
    
    Inputs:
        min_price: The minimum price to consider.
    Outputs
        (min, max) tuple. A tuple containing the minimum and maximum price range."""
    
    # Occasionally Airbnb will not return the room count data and the BeautifulSoup selector will return
    # an empty list. The following loop will relaod the page until the room counts are returned. It will
    # try 5 times.
    for i in range(5):
        url = format_url(base_url, driver, start_date=start_date, end_date=end_date, min_price=min_price, max_price=max_price)
        try:
            soup = get_page(url, driver)
            room_count = soup.select('div._1snxcqc')[0].string.split()[0]
            room_count.replace('+', '')
            room_count = int(room_count.replace('+', ''))
            break
        except Exception as e:
            print(e)
    
    return room_count


def find_optimum_range(base_url, driver, start_date, end_date, min_price=0, max_price=20):
    """Finds the optimum praice range to get less than 300 stays.
    
    This function will:
    1. Get the number of rooms at the given price range.
    2. If more than 300 rooms are returned it will decrease the max_price until a value less than 300 rooms is returned.
    3. If less than 300 rooms are returned it will increase the max_price until more than 300 rooms are returned.
    4. Steps 2 & 3 will be repeated until a price range that will yield the largest number of rooms less than 300 is found."""
    
    top = max_price + 500
    bottom = min_price
    room_count = find_room_count_for_range(base_url, driver, start_date=start_date, end_date=end_date, min_price=min_price, max_price=max_price)
    
    while(room_count >= 300 or (top > max_price + 1 and room_count > 0)):
        if room_count >= 300:
            top = max_price
            max_price = bottom + (max_price - bottom) // 2
        else:
            bottom = max_price
            max_price = max_price + (top - max_price) // 2
        print(min_price, max_price)
        room_count = find_room_count_for_range(base_url, driver, start_date=start_date, end_date=end_date, min_price=min_price, max_price=max_price)
    
    return (room_count, min_price, max_price)
            
def get_price_ranges(base_url, driver, start_date, end_date, min_price=0, max_price=0):
    price_ranges = []
    last_count = 1
    while(last_count > 0):
        current_range = find_optimum_range(base_url, driver, start_date, end_date, min_price, max_price)
        if current_range[0] > 0:
            price_ranges.append(current_range)
            min_price = current_range[2] + 1
            max_price = current_range[2] + 1
        last_count = current_range[0]
    
    return price_ranges


def to_int(string):
    """Removes non-digit characters from a string and attempts to cast it as a int."""
    return int(re.sub(r'\D', '', string))

def number_of_stays_page_bottom(soup):
    nbr_of_stays_tag = soup.select('div._1h559tl')[0].contents
    n_to_n_of_stays = filter(lambda x: re.search(r'\d+', x), map(lambda x: x.string, nbr_of_stays_tag)) # and re.search(r'\d+', x), nbr_of_stays_tag)
    n_to_n_of_stays = map(lambda x: x.replace('of', '').replace('places to stay', ''), n_to_n_of_stays)
    n_to_n_of_stays = list(n_to_n_of_stays)
    n_to_n_of_stays = re.sub(r' +', ' ', ' '.join(n_to_n_of_stays))
    n_to_n_of_stays = list(map(to_int, n_to_n_of_stays.split()))
    return n_to_n_of_stays

def get_listings_from_json(soup):
    """Retrieves a json object from the page source. The json object contains
    loads of airbnb room data. It isn't always present. The reason is isn't
    always there hasn't been worked out yet."""
    # Below is the tag that contains the json object with a bunch of room data.
    # <script data-state="true" id="data-state" type="application/json">
    try:
        json_object = json.loads(soup.find(id='data-state').string)
    except Exception as e:
        json_object = {}
        raise e
    # Below is how the room data is burried in the json object. It would be
    # possible to put all this on one line but I think this better shows how deep
    # The information is burried and the path to it.
    rooms = json_object['niobeClientData']
    rooms = rooms['__niobe_denormalized']
    rooms = rooms['queries']
    rooms = rooms[0][1]
    rooms = rooms['dora']
    rooms = rooms['exploreV3']
    rooms = rooms['sections']
    rooms = rooms[0]
    rooms = rooms['items']
    listings = []
    for room in rooms:
        new_room = room['listing']
        new_room.update(room['pricingQuote'])
        listings.append(new_room)
    return listings


def get_listings_data(listings, keys, listing_data):
    """Returns a dictionary of lists. Each key is the name of the data element
    in the list.

    TODO: This seems bad form. Think about rewriting this function to return
    a dictionary of key value pairs instead of accepting, modifying and returning
    a dictionary."""

    for listing in listings:
        for key in keys:
            listing_data[key].append(find_key(listing, key))

    return listing_data

def linear_distance(latitude1, longitude1, latitude2, longitude2):
    """Calculates the distance between two point with values given in
    latitude and longitude.
    Source: https://support.sisense.com/hc/en-us/articles/230644288-Calculate-Distance-Between-Two-Points-Using-Latitude-and-Longitude
    # Acos(sin(PI()*latitude1/180.0)*sin(PI()*latitude2/180.0)+cos(PI()*latitude1/180.0)*cos(PI()*latitude2/180.0)*cos(PI()*longitude1/180.0-PI()*longitude2/180.0))*6378"""
    PI = 3.14159
    distance = acos( sin(PI * latitude1 / 180.0) * \
                     sin(PI * latitude2 / 180.0) + \
                     cos(PI * latitude1 / 180.0) * \
                     cos(PI * latitude2 / 180.0) * \
                     cos(PI * longitude1 / 180.0 - \
                     PI * longitude2 / 180.0) ) * 6378
    return distance



class TestAirbnbScrapes(unittest.TestCase):

    maxDiff = None

    def setUp(self):
        self.driver = setup_webdriver(width=1100, height=1020)
        self.ORIGINAL_URL = 'https://www.airbnb.com/s/Bogota--Colombia/homes?tab_id=home_tab&refinement_paths%5B%5D=%2Fhomes&place_id=ChIJKcumLf2bP44RFDmjIFVjnSM&source=structured_search_input_header&search_type=pagination&federated_search_session_id=03d88384-9106-466f-a2f1-4150e425ada3&query=Bogota%2C%20Colombia&checkin=2020-08-09&checkout=2020-08-12&price_min=15&price_max=35&room_types%5B%5D=Entire%20home%2Fapt&section_offset=2&items_offset=40'

    def test_driverSetup(self):
        """Tests to make sure the webdriver object gets created correctly."""
        # self.assertIsInstance(self.driver, selenium.webdriver.chrome.webdriver.WebDriver)
        self.assertEqual(self.driver.get_window_size(), {'width': 1100, 'height': 1015})

    def test_formatUrl(self):
        """Tests URL formatting"""
        self.assertEqual(format_url(BASE_URL, 
                                    offset=40,
                                    start_date=datetime(2020, 8, 9),
                                    end_date=datetime(2020, 8, 12),
                                    min_price=15,
                                    max_price=35), 
                         self.ORIGINAL_URL)
    
    def test_getPage(self):
        url = format_url(BASE_URL,
                         offset=40, 
                         start_date=datetime.now() + timedelta(days=90),
                         end_date=datetime.now() + timedelta(days=93),
                         min_price=20,
                         max_price=40)
        soup = get_page(url, self.driver)
        self.assertIsInstance(soup, bs4.BeautifulSoup)
        self.assertTrue(len(soup.select('div')) > 0)
    
    def test_staysOnPage(self):
        url = format_url(BASE_URL,
                         offset=40, 
                         start_date=datetime.now() + timedelta(days=90),
                         end_date=datetime.now() + timedelta(days=93),
                         min_price=20,
                         max_price=40)
        
    def test_findRoomCountForRange(self):
        rooms = find_room_count_for_range(BASE_URL, 
                                          self.driver,
                                          start_date=datetime.now() + timedelta(days=90),
                                          end_date=datetime.now() + timedelta(days=93),
                                          min_price=0,
                                          max_price=100)
        self.assertTrue(rooms > 299)
        
    def test_findOptimumRange(self):
        optimum_range = find_optimum_range(BASE_URL, 
                                           self.driver, 
                                           start_date=datetime.now() + timedelta(days=90),
                                           end_date=datetime.now() + timedelta(days=93),
                                           min_price=0,
                                           max_price=20)
        print('Room Count:', optimum_range[0])
        print('Min Price:', optimum_range[1])
        print('Max Price:', optimum_range[2])
        self.assertIsInstance(optimum_range[0], int)
        self.assertIsInstance(optimum_range[1], int)
        self.assertIsInstance(optimum_range[2], int)
        self.assertTrue(optimum_range[0] > 0)
        self.assertTrue(optimum_range[1] >= 0)
        self.assertTrue(optimum_range[2] > 0)

    def test_getPriceRanges(self):
        price_ranges = get_price_ranges(BASE_URL, 
                                        self.driver, 
                                        start_date=datetime.now() + timedelta(days=90),
                                        end_date=datetime.now() + timedelta(days=93),
                                        min_price=0,
                                        max_price=20)
        print(price_ranges)
        self.assertIsInstance(price_ranges, list)
        self.assertTrue(len(price_ranges) > 0)

    def test_getListings(self):
        url = format_url(BASE_URL,
                         offset=40, 
                         start_date=datetime.now() + timedelta(days=90),
                         end_date=datetime.now() + timedelta(days=93),
                         min_price=20,
                         max_price=40)
        listings = get_listings_from_json(get_page(url, self.driver, delay=10))
        self.assertEqual(len(listings), 20)
        for listing in listings:
            self.assertIsInstance(listing, dict)

    def test_getListingData(self):
        url = format_url(BASE_URL,
                         offset=40, 
                         start_date=datetime.now() + timedelta(days=90),
                         end_date=datetime.now() + timedelta(days=93),
                         min_price=20,
                         max_price=40)
        listings = get_listings_from_json(get_page(url, self.driver, delay=10))
        keys = ['lat', 'lng', 'id']
        listing_data = get_listings_data(listings, keys, defaultdict(list))
        print('=' * 30)
        print(listing_data)
        print('=' * 30)
        self.assertIsInstance(listing_data, dict)
        for key in keys:
            self.assertTrue(key in listing_data)

    def test_linearDistance(self):
        # First point is Broomfield Colorado
        latitude1 = 39.923988
        longitude1 = -105.081657
        # Second point is Salt Lake City Utah
        latitude2 = 40.760780
        longitude2 = -111.891045
        distance = linear_distance(latitude1, longitude1, latitude2, longitude2)
        self.assertTrue(583 < distance < 586)
        latitude1 = 4.6585
        longitude1 = -74.0935
        latitude2 = 4.6057
        longitude2 = -74.0555
        distance = linear_distance(latitude1, longitude1, latitude2, longitude2)
        print(distance)



    def tearDown(self):
        self.driver.close()

if __name__ == '__main__':

    unittest.main()
