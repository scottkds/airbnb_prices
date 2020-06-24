# Imports
import pandas as pd
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import re
import json
import time
from collections import defaultdict

def number_of_stays_page_bottom(soup):
    nbr_of_stays_tag = soup.select('div._1h559tl')[0].contents
    n_to_n_of_stays = filter(lambda x: re.search(r'\d+', x), map(lambda x: x.string, nbr_of_stays_tag)) # and re.search(r'\d+', x), nbr_of_stays_tag)
    n_to_n_of_stays = map(lambda x: x.replace('of', '').replace('places to stay', ''), n_to_n_of_stays)
    n_to_n_of_stays = list(n_to_n_of_stays)
    n_to_n_of_stays = re.sub(r' +', ' ', ' '.join(n_to_n_of_stays))
    n_to_n_of_stays = list(map(int, n_to_n_of_stays.split()))
    return n_to_n_of_stays

if __name__ == '__main__':

    with open('data/airbnb_list_src.txt', 'r', encoding='utf-8') as f:
        page_source = f.read()
    
    soup = BeautifulSoup(page_source, features='html.parser')

    print(number_of_stays_page_bottom(soup))
