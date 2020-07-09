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
import unittest

URL = 'https://www.airbnb.com/s/Bogot%C3%A1-~-Bogota--Colombia/homes?tab_id=home_tab&refinement_paths%5B%5D=%2Fhomes&place_id=ChIJKcumLf2bP44RFDmjIFVjnSM&source=structured_search_input_header&search_type=filter_change&query=Bogota%2C%20Colombia&checkin=2020-09-05&checkout=2020-09-08&room_types%5B%5D=Entire%20home%2Fapt'

driver = selenium.webdriver.Firefox()
driver.set_window_size(1100, 1020)
driver.get(URL)