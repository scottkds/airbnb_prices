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
    for i in range(3):
        try:
            elem = driver.find_element_by_css_selector('._52mr6fl')
        except:
            #print('Failed with ._52mr6fl')
            pass
        try:
            elem = driver.find_element_by_css_selector('._1v4ygly5')
        except:
            #print('Failed with ._1v4ygly5')
            pass
        try:
            elem = driver.find_element_by_css_selector('._13e0raay')
        except:
            print('Failed with ._13e0raay')
            pass
        time.sleep(10)
    return elem

def get_amenities(page_source):
    """Gets the amenities listed after clicking he "Show All Amenities" button
    on the page. Returns a list."""
    soup = bs4.BeautifulSoup(page_source, features='html.parser')
    amenities = soup.select('div._vzrbjl')
    amenities_list = [amenity.contents[0] for amenity in amenities \
                        if isinstance(amenity.contents[0], bs4.element.NavigableString)]
    return amenities_list

def get_rooms(soup):
    """Returns the number of guests, bedrooms, beds, and bathrooms the stay
    has."""
    guests, bedrooms, beds, baths = (0, 0, 0, 0)
    div = soup.select('div._tqmy57')
    spans = div[0].select('span')
    span_strings = [span.string for span in spans]
    #pdb.set_trace()
    for string in span_strings:
        if re.search(r'guest', string):
            guests = int(re.sub(r'\D+', '', string))
        elif re.search(r'bedroom', string):
            bedrooms = int(re.sub(r'\D+', '', string))
        elif re.search(r'Studio', string):
            bedrooms = 0
        elif re.search(r'bath', string):
            baths = int(re.sub(r'\D+', '', string))
        elif re.search(r'Half-bath', string):
            baths = 0.5
        elif re.search(r'bed', string):
            beds = int(re.sub(r'\D+', '', string))
    
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
                print(e)
        else:
            try:
                stars_reviews = stars_and_review_cnt[0].split()
                stars = float(stars_reviews[0])
                reviews = int(re.sub(r'\D+', '', stars_reviews[1]))
            except Exception as e:
                print(e)
                stars = 0
                reviews = 0
        return (stars, reviews)

    def get_cleaning_fee(cleaning_fee_tag):
        """Gets the cleaning fee from the price summary block."""
        cleaning_fee = 0
        try:
            assert cleaning_fee_tag != []
        except:
            # Sometimes I just can't find the tags in the page_source.
            # I will filter out rooms with a cleaning fee of 999999
            cleaning_fee = 999999
        for item in cleaning_fee_tag:
            if item.find_all(string='Cleaning fee'):
                cleaning_fee = item.select('span._ra05uc')[0].string
                cleaning_fee = int(cleaning_fee.replace('$', ''))
                
        return cleaning_fee

    #div = soup.select('div._ud8a1c')[0]
    try:
        price = get_price_as_int(soup.select('span._pgfqnw')[0])
    except IndexError as e:
        raise e
    try:
        stars, reviews  = get_stars_and_reviews(soup.select('button._1wlymrds')[0])
    except IndexError:
        stars, reviews = (0, 0)
    except TypeError:
        stars = 0
        reviews = soup.select('span._bq6krt')[0]
        reviews = re.sub(r'\D+', '', reviews)

    cleaning_fee = get_cleaning_fee(soup.select('li._ryvszj') + \
                                    soup.select('li._puvex1k'))
    try:
        long_stay_tag = soup.select('span._l1ngr4')[0]
        long_stay_discount = int(re.sub(r'\D+', '', long_stay_tag.string))
    except IndexError:
        long_stay_discount = 0
    superhost = is_super_host(soup.select('span._nu65sd'))

    return (price, stars, reviews, cleaning_fee, long_stay_discount, superhost)


def get_id(link):
    room_id_match = re.search(r'https://www.airbnb.com/rooms(/plus)?/(\d+)\?', link) 
    if room_id_match.group(1) == '/plus':
        try:
            room_id = int(room_id_match.group(2))
        except Exception as e:
            raise e
    else:
        try:
            room_id = int(room_id_match.group(1))
        except Exception as e:
            raise e

    return room_id

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

    def test_getLink(self):
        some_url = 'https://www.airbnb.com/rooms/30691310?location=Bogota%2C%20Colombia&check_in=2020-10-01&check_out=2020-10-05&source_impression_id=p3_1595191777_n7mbZbfdoVOXHj8H&guests=1&adults=1'
        self.assertEqual(get_id(some_url), 30691310)

    def tearDown(self):
        self.driver.close()


if __name__ == '__main__':

    unittest.main()
