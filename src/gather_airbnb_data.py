import pandas as pd
from airbnb_lib import get_price_ranges, setup_webdriver
import airbnb_page_components_lib as pc
from datetime import datetime, timedelta
import pickle
import sys

BASE_URL = pc.BASE_URL
START_DATE = datetime(2020, 10, 1)
END_DATE = datetime(2020, 10, 5)

driver = setup_webdriver(width=1100, height=1020)

if '--use-pickle' in sys.argv:
    with open('price_range.pkl', 'rb') as f:
        price_ranges = pickle.load(f)
    f.close()
else:
    #price_ranges = get_price_ranges(BASE_URL, driver, START_DATE, END_DATE, 0, 50)
    price_ranges = [x for x in range(10)]

    with open('price_range.pkl', 'wb') as f:
        pickle.dump(price_ranges, f)
    f.close()


print(price_ranges)

driver.close()
