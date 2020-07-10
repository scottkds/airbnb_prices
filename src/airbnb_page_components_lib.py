from airbnb_lib import BASE_URL, format_url, get_page, setup_webdriver
import pickle
import unittest
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import time
import bs4
import selenium
import re
import pdb


# pdb.set_trace()

def get_page_stays_list(soup):
    stays = soup.select('div._8ssblpx')
    return stays

def relative_link(stay):
    link = stay.select('a._gjfol0')
    assert len(link) == 1
    return link[0].get('href')

def get_amenities_elem(driver):

    try:
        elem = driver.find_element_by_css_selector('._52mr6fl')
    except:
        # print('Failed with ._52mr6fl')
        pass
    try:
        elem = driver.find_element_by_css_selector('._1v4ygly5')
    except:
        # print('Failed with ._1v4ygly5')
        pass

    return elem

def get_amenities(soup):
    amenities = soup.select('div._vzrbjl')
    amenities_list = [amenity.contents[0] for amenity in amenities \
                        if isinstance(amenity.contents[0], bs4.element.NavigableString)]
    return amenities_list

def get_rooms(soup):
    div = soup.select('div._tqmy57')
    spans = div[0].select('span')
    span_strings = [re.sub(r'\D+', '', str(span.string)) for span in spans]
    guests = int(span_strings[0])
    bedrooms = int(span_strings[2])
    beds = int(span_strings[4])
    baths = int(span_strings[6])
    # pdb.set_trace()
    return (guests, bedrooms, beds, baths)

class TestPageComponents(unittest.TestCase):

    driver = setup_webdriver(width=1100, height=1020)
    soup = get_page(format_url(BASE_URL,
                              offset=0, 
                              start_date=datetime.now() + timedelta(days=90),
                              end_date=datetime.now() + timedelta(days=93),
                              min_price=0,
                              max_price=20), driver)

    def test_srcType(self):
        self.assertIsInstance(self.soup, bs4.BeautifulSoup)

    def test_staysList(self):
        self.assertEqual(len(get_page_stays_list(self.soup)), 20)

    def test_stayLink(self):
        stays = get_page_stays_list(self.soup)
        link = relative_link(stays[0])
        self.assertIsInstance(link, str)
        self.assertEqual(link[:7], '/rooms/')

    def test_getAmenitiesElem(self):
        stays = get_page_stays_list(self.soup)
        link = 'https://www.airbnb.com' + relative_link(stays[0])
        self.driver.get(link)
        time.sleep(5)
        elem = get_amenities_elem(self.driver)
        elem.click()
        time.sleep(1)
        soup = bs4.BeautifulSoup(self.driver.page_source, features='html.parser')
        print(get_amenities(soup))

    def test_getRooms(self):
        stays = get_page_stays_list(self.soup)
        link = 'https://www.airbnb.com' + relative_link(stays[0])
        self.driver.get(link)
        time.sleep(5)
        soup = bs4.BeautifulSoup(self.driver.page_source, features='html.parser')
        rooms = get_rooms(soup)
        self.assertIsInstance(rooms[0], int)
        self.assertIsInstance(rooms[1], int)
        self.assertIsInstance(rooms[2], int)
        self.assertIsInstance(rooms[3], int)

if __name__ == '__main__':
    
    driver = setup_webdriver(width=1100, height=1020)
    
    src = get_page(format_url(BASE_URL,
                              offset=0, 
                              start_date=datetime.now() + timedelta(days=90),
                              end_date=datetime.now() + timedelta(days=90),
                              min_price=0,
                              max_price=20), driver)

    with open('/home/scott/projects/mp2/test_data/airbnb_listings.html', 'w+') as f:
        f.write(src.prettify())
