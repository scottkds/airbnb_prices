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
    """Returns the individual elements that comprise the stays listed on a page.
    There should be 20 of them."""
    stays = soup.select('div._8ssblpx')
    return stays

def relative_link(stay):
    """Gets the realtive link for the stay. It is of the form /rooms/idnumber/..."""
    link = stay.select('a._gjfol0')
    assert len(link) == 1
    return link[0].get('href')

def get_amenities_elem(driver):
    """Get the amenities element for the stay."""
    try:
        elem = driver.find_element_by_css_selector('._52mr6fl')
    except:
        print('Failed with ._52mr6fl')
        pass
    try:
        elem = driver.find_element_by_css_selector('._1v4ygly5')
    except:
        print('Failed with ._1v4ygly5')
        pass
    try:
        elem = driver.find_element_by_css_selector('._13e0raay')
    except:
        print('Failed with ._13e0raay')
        pass
    return elem

def get_amenities(soup):
    """Gets the amenities listed after clicking he "Show All Amenities" button
    on the page. Returns a list."""
    amenities = soup.select('div._vzrbjl')
    amenities_list = [amenity.contents[0] for amenity in amenities \
                        if isinstance(amenity.contents[0], bs4.element.NavigableString)]
    return amenities_list

def get_rooms(soup):
    """Returns the number of guests, bedrooms, beds, and bathrooms the stay
    has."""
    div = soup.select('div._tqmy57')
    spans = div[0].select('span')
    span_strings = [re.sub(r'\D+', '', str(span.string)) for span in spans]
    guests = int(span_strings[0])
    bedrooms = int(span_strings[2])
    beds = int(span_strings[4])
    baths = int(span_strings[6])
    return (guests, bedrooms, beds, baths)

def get_price_summary_info(soup):
    """Gets all of the HTML in the pricing summary block. Embedded functions
    extract the desired pieces of information: price, stars, cleaning fee,
    long stay discount, and superhost."""

    def is_super_host(tags):
        """Checks for "Superhost" text in the input tags. Returns true if found."""
        for tag in tags:
            if str(tag.string) == 'Superhost':
                return True
        return False

    def get_price_as_int(price_tag):
        """Parses out the price for the stay and returns it as an int."""
        price = str(price_tag.string)
        price = price.replace('$', '')
        price = int(price)
        return price

    def get_stars_and_reviews(stars_tag):
        """Gets the average number of stars that previous reviewers have given
        the stay and the the review count."""
        stars_and_review_cnt = stars_tag.contents

        # Airbnb can put one or two span elements or a single button element in
        # the element that gets passed to this function. The following if statement
        # deals with those two cases.
        if len(stars_and_review_cnt) > 1:
            try:
                stars = float(stars_and_review_cnt[0].string)
                reviews = int(re.sub(r'\D+', '', stars_and_review_cnt[1].string))
            except Exception as e:
                print('CANNOT EXTRACT STARS AND REVIEWS!!')
                stars = 0
                reviews = 0
                raise e
        else:
            try:
                stars_reviews = stars_and_review_cnt[0].split()
                stars = float(stars_reviews[0])
                reviews = int(re.sub(r'\D+', '', stars_reviews[1]))
            except Exception as e:
                raise e

        return (stars, reviews)

    div = soup.select('div._ud8a1c')[0]
    price = get_price_as_int(soup.select('span._pgfqnw')[0])
    stars, reviews  = get_stars_and_reviews(soup.select('button._1wlymrds')[0])
    #stars  = soup.select('button._1wlymrds')[0]
    cleaning_fee = soup.select('span._ra05uc')[0]
    try:
        long_stay_discount = soup.select('span._l1ngr4')[0]
    except IndexError:
        long_stay_discount = 0
    superhost = is_super_host(soup.select('span._nu65sd'))

class TestPageComponents(unittest.TestCase):
    """ Unit tests for page components."""

    def setUp(self):
        self.driver = setup_webdriver(width=1100, height=1020)
        self.soup = get_page(format_url(BASE_URL,
                                  offset=0, 
                                  start_date=datetime.now() + timedelta(days=90),
                                  end_date=datetime.now() + timedelta(days=93),
                                  min_price=0,
                                  max_price=20), self.driver)

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
        """This test will take a few minutes to run."""
        stays = get_page_stays_list(self.soup)
        for stay in stays:
            link = 'https://www.airbnb.com' + relative_link(stay)
            self.driver.get(link)
            time.sleep(5)
            elem = get_amenities_elem(self.driver)
            elem.click()
            time.sleep(1)
            soup = bs4.BeautifulSoup(self.driver.page_source, features='html.parser')
            amenities = get_amenities(soup)
            self.assertIsInstance(amenities, list)
            self.driver.back()

    def test_getRooms(self):
        stays = get_page_stays_list(self.soup)
        link = 'https://www.airbnb.com' + relative_link(stays[0])
        self.driver.get(link)
        time.sleep(5)
        soup = bs4.BeautifulSoup(self.driver.page_source, features='html.parser')
        rooms = get_rooms(soup)
        self.assertIsInstance(rooms[0], int)
        self.assertTrue(rooms[0] > 0)
        self.assertIsInstance(rooms[1], int)
        self.assertTrue(rooms[1] > 0)
        self.assertIsInstance(rooms[2], int)
        self.assertTrue(rooms[2] > 0)
        self.assertIsInstance(rooms[3], int)
        self.assertTrue(rooms[3] > 0)

    def test_getPrices(self):
        stays = get_page_stays_list(self.soup)
        link = 'https://www.airbnb.com' + relative_link(stays[0])
        self.driver.get(link)
        time.sleep(5)
        soup = bs4.BeautifulSoup(self.driver.page_source, features='html.parser')
        rooms = get_price_summary_info(soup)

    def tearDown(self):
        self.driver.close()


if __name__ == '__main__':

    unittest.main()
