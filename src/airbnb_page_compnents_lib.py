from airbnb_lib import BASE_URL, format_url, get_page, setup_webdriver
import pickle
import unittest
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import time
import pdb


pdb.set_trace()

class TestPageComponents(unittest.TestCase):
    pass


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
