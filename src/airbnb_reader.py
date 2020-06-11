from selenium import webdriver
from bs4 import BeautifulSoup
import time

driver = webdriver.Chrome()
time.sleep(5)
window = driver.window_handles[0]
driver.switch_to.window(driver.window_handles[0])
link = 'https://www.airbnb.com/s/Bogota--Colombia/homes?tab_id=all_tab&refinement_paths%5B%5D=%2Fhomes&query=Bogota%2C%20Colombia&place_id=ChIJKcumLf2bP44RFDmjIFVjnSM&checkin=2020-06-14&checkout=2020-06-28&source=structured_search_input_header&search_type=search_query'
link = 'https://www.airbnb.com/rooms/13516185?location=Bogota%2C%20Colombia&check_in=2020-06-14&check_out=2020-06-28&source_impression_id=p3_1590372927_i1WyHyNErr07fsxz&guests=1&adults=1'
driver.get(link)
time.sleep(5)
divs = driver.find_elements('tag name', 'div')

with open('../data/basic_page_info.txt', 'w+') as f:
    for div in divs:
        f.write(str((div.tag_name, div.text)))
        f.write('\n')

