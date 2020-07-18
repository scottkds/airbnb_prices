import pandas as pd
from airbnb_lib import get_price_ranges, setup_webdriver
import airbnb_page_components_lib as pc
from datetime import datetime, timedelta

BASE_URL = pc.BASE_URL
START_DATE = datetime(2020, 10, 1)
END_DATE = datetime(2020, 10, 5)

driver = setup_webdriver(width=1100, height=1020)
price_ranges = get_price_ranges(BASE_URL, driver, START_DATE, END_DATE, 0, 50)

print(price_ranges)


